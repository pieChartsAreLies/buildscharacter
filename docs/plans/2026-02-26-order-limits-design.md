# Order Limits Design: Webhook Order Guard (Fail-Closed)

**Date**: 2026-02-26
**Status**: Approved (revised after Gemini adversarial review)
**Problem**: Printful charges the store owner for production costs on chargebacks. A fraudulent bulk order (e.g., 1000 stickers) could create significant financial exposure with no recourse.
**Solution**: Fail-closed order guard service. Printful holds all orders as drafts. A webhook-driven service confirms orders that pass validation rules; orders that fail or aren't processed stay as unconfirmed drafts requiring manual review.

## Architecture (Fail-Closed)

The key design principle: **orders never proceed to production unless explicitly confirmed by the Order Guard.** If the service is down, orders sit safely as drafts.

```
Customer places order on buildscharacter.printful.me
            |
            v
   Printful processes payment, holds order as DRAFT
            |
            v
   Printful fires webhook
            |
            v
   CF Tunnel (webhooks.buildscharacter.com)
            |
            v
   Order Guard Service (CT 255, port 8100)
     FastAPI, ~200 lines
            |
            +--- Validate HMAC signature (X-Printful-Signature)
            +--- Return 200 OK immediately
            +--- Process in background:
            |      Parse order, evaluate rules:
            |        - Production cost <= $50?
            |        - Per-item qty <= 3?
            |        - Hourly order velocity <= 5?
            |
            +--- ALL PASS --> Confirm order via POST /orders/{id}/confirm
            |                 Log to PG + Telegram "Order confirmed"
            |
            +--- ANY FAIL --> Leave as draft (do NOT confirm)
            |                 Log to PG
            |                 Telegram "Order held: [reason]"
            |
            +--- SERVICE DOWN --> Order stays as draft
                                  Manual review via Printful dashboard
```

### Why Fail-Closed?

Previous design (v1) cancelled bad orders. If the service went down, orders proceeded unchecked, defeating the purpose. By inverting the model, downtime = safety. Orders that aren't explicitly confirmed never reach production.

## Components

| Component | Location | Description |
|-----------|----------|-------------|
| Order Guard Service | CT 255, systemd unit | FastAPI webhook listener + order evaluator |
| PostgreSQL table | CT 201, `hobson.order_events` | Audit log of all orders and actions |
| Printful Store Setting | Printful Dashboard | "Manually approve orders" / draft mode enabled |
| Printful Webhook | Printful Dashboard | POST to CF Tunnel URL on order events |
| CF Tunnel route | Cloudflare | Maps public URL to CT 255:8100 |
| Telegram notifications | Bob's chat | Order summaries and hold alerts |
| Uptime Kuma monitor | CT 182 | HTTP health check on Order Guard |

## Order Evaluation Rules

Three rules evaluated on every incoming order:

1. **Per-order production cost cap**: Your production cost (not retail price) must not exceed $50. Printful webhook payloads include a `costs` object with what you pay vs. `retail_costs` with what the customer pays. This prevents blocking legitimate $60 retail orders where your cost is $25.
2. **Per-item quantity cap**: No single line item can have more than 3 units.
3. **Hourly velocity cap**: No more than 5 orders per rolling hour across all customers. Catches card-testing attacks that use many small orders to stay under per-order limits.

If all rules pass: confirm the order for fulfillment.
If any rule fails: leave the order as a draft and alert via Telegram for manual review.

Rules are configurable via environment variables.

## Webhook Handling

**Endpoint**: `POST /printful/webhook`

**Authentication (mandatory)**:
- Validate the `X-Printful-Signature` HMAC header against the webhook secret configured in Printful's dashboard
- Reject requests with missing or invalid signatures (return 401)

**Async processing**:
- Validate signature and return 200 OK immediately
- Process order evaluation in a FastAPI BackgroundTask
- This prevents Printful webhook timeouts if the Printful API is slow during confirmation

**Idempotency**:
- Use `INSERT ... ON CONFLICT (printful_order_id, event_type) DO NOTHING` on database writes
- If no rows affected (duplicate webhook), skip processing and return 200 OK
- Prevents IntegrityErrors on Printful retries

**Security**:
- HMAC signature validation (required, not optional)
- Accept only POST requests
- Rate limit: reject if > 10 requests/minute (defense against non-Printful traffic)

## Notification Behavior

**On order confirmed (passes all rules)**:
- Confirm via `POST /orders/{id}/confirm` Printful API
- Telegram message: "Order #X confirmed: [items], your cost $Y, retail $Z"
- Log to `hobson.order_events`

**On order held (fails any rule)**:
- Leave order as draft (no API call needed)
- Telegram message with: order ID, production cost, retail total, item breakdown, which rule(s) triggered
- Log to `hobson.order_events`
- You can manually confirm or cancel via Printful dashboard after review

**On errors (API failure, parse error, etc.)**:
- Telegram alert with error details
- Log raw webhook payload for debugging
- Order stays as draft (safe default)

## Database Schema

```sql
CREATE TABLE hobson.order_events (
    id SERIAL PRIMARY KEY,
    printful_order_id BIGINT NOT NULL,
    event_type TEXT NOT NULL,       -- 'order_confirmed', 'order_held', 'error'
    production_cost NUMERIC(10,2),  -- what you pay Printful
    retail_total NUMERIC(10,2),     -- what customer paid
    item_count INTEGER,
    rule_violated TEXT,             -- NULL if confirmed; 'max_cost', 'max_item_qty', 'velocity' if held
    raw_payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(printful_order_id, event_type)
);

CREATE INDEX idx_order_events_created_at ON hobson.order_events(created_at);
```

The `created_at` index supports the velocity check query: `SELECT COUNT(*) FROM hobson.order_events WHERE event_type = 'order_confirmed' AND created_at > NOW() - INTERVAL '1 hour'`.

## Configuration

Environment variables on CT 255:

```
ORDER_MAX_PRODUCTION_COST=50.00
ORDER_MAX_ITEM_QTY=3
ORDER_MAX_HOURLY_VELOCITY=5
PRINTFUL_API_KEY=<from Bitwarden>
PRINTFUL_WEBHOOK_SECRET=<from Bitwarden>
TELEGRAM_BOT_TOKEN=<Bob's token>
TELEGRAM_CHAT_ID=<user's chat>
DATABASE_URL=postgresql://hobson:<password>@192.168.2.67:5432/project_data
ORDER_GUARD_PORT=8100
```

## Cloudflare Tunnel

Printful needs a public URL for webhooks. CT 255 is internal-only.

- Create or extend a CF Tunnel to route `webhooks.buildscharacter.com` to `localhost:8100` on CT 255
- Configure the webhook URL in Printful's dashboard: `https://webhooks.buildscharacter.com/printful/webhook`
- Check during implementation whether CT 255 already has a cloudflared instance

## Printful Store Configuration

**Required manual step**: Enable "Manually approve orders" in Printful store settings so orders are held as drafts by default. This is the foundation of the fail-closed architecture. Without this setting, the entire design doesn't work.

**Verification**: After enabling, place a test order and confirm it appears as a draft in the Printful dashboard, not as auto-confirmed.

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Printful retries webhook | Idempotent: INSERT ON CONFLICT DO NOTHING, return 200 |
| Order Guard is down | Orders stay as drafts. Safe. Manual review via dashboard. |
| Printful confirm API fails | Telegram alert. Order stays as draft for manual confirmation. |
| Velocity attack (many small orders) | Hourly cap of 5 orders. Orders beyond limit held as drafts. |
| Legitimate high-value order held | Telegram alert shows details. Manual confirm via Printful dashboard. |
| Service comes back after downtime | Pending drafts still in Printful dashboard for manual review. Webhook retries may trigger processing. |

## Not In Scope

- Custom checkout/cart (over-engineered for current stage)
- Per-customer rolling limits by email (v2 if needed)
- Payment processing (Printful handles this)
- Telegram interactive approve buttons (nice-to-have for v2)
- Customer allow-listing for repeat buyers (v2)

## Risk Assessment

**Residual risk**: Minimal. The fail-closed design means downtime = safety. The only scenario where a fraudulent order proceeds is if someone manually confirms it in the Printful dashboard.

**Refund handling**: Since we hold orders as drafts rather than cancelling confirmed orders, the refund question is mostly moot. Draft orders haven't been charged (or if payment is collected, Printful's draft cancellation process handles refunds). This needs verification during implementation.

**Production cost accuracy**: The $50 cap is based on Printful's `costs` object in the webhook payload. This should reflect actual production + shipping cost to you, not retail price. Verify the payload structure during implementation with a test order.

## Adversarial Review Notes

This design was revised after Gemini adversarial review. Key changes from v1:
- Inverted from "cancel bad" to "confirm good" (fail-closed)
- Mandatory HMAC webhook authentication (was optional)
- Production cost basis instead of retail total
- Async webhook processing (return 200 immediately)
- Idempotency via ON CONFLICT DO NOTHING (was missing)
- Hourly velocity check (was not in scope)
