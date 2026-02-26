# Order Limits Design: Webhook Auto-Cancel

**Date**: 2026-02-26
**Status**: Approved
**Problem**: Printful charges the store owner for production costs on chargebacks. A fraudulent bulk order (e.g., 1000 stickers) could create significant financial exposure with no recourse.
**Solution**: Webhook-driven order monitoring service that auto-cancels orders exceeding configurable thresholds.

## Architecture

```
Customer places order on buildscharacter.printful.me
            |
            v
   Printful processes payment
            |
            v
   Printful fires order_created webhook
            |
            v
   CF Tunnel (webhooks.buildscharacter.com)
            |
            v
   Order Guard Service (CT 255, port 8100)
     FastAPI, ~150 lines
            |
            +--- Parse webhook payload
            +--- Evaluate rules:
            |      - Total <= $50?
            |      - Per-item qty <= 3?
            |
            +--- PASS --> Log to PG + Telegram "New order"
            |
            +--- FAIL --> Cancel via Printful API
                           Log to PG
                           Telegram "Order cancelled: [reason]"
```

## Components

| Component | Location | Description |
|-----------|----------|-------------|
| Order Guard Service | CT 255, systemd unit | FastAPI webhook listener + order evaluator |
| PostgreSQL table | CT 201, `hobson.order_events` | Audit log of all orders and actions |
| Printful Webhook | Printful Dashboard | POST to CF Tunnel URL on order_created |
| CF Tunnel route | Cloudflare | Maps public URL to CT 255:8100 |
| Telegram notifications | Bob's chat | Order summaries and cancellation alerts |

## Order Evaluation Rules

Two rules evaluated on every incoming order:

1. **Per-order dollar cap**: Total order cost (items + shipping) must not exceed $50
2. **Per-item quantity cap**: No single line item can have more than 3 units

If either rule is violated, the order is cancelled. Rules are configurable via environment variables.

## Webhook Handling

**Endpoint**: `POST /printful/webhook`

**Payload**: Printful sends a JSON payload with order details including items, quantities, and costs.

**Idempotency**: The service checks if an order ID has already been processed before taking action. Printful retries failed webhook deliveries, so duplicate handling is required.

**Security**:
- Accept only POST requests
- Validate expected payload structure
- Rate limit: reject if > 10 requests/minute
- Optional: secret token as URL parameter for basic authentication

## Notification Behavior

**On cancellation (order exceeds limits)**:
- Cancel via `DELETE /orders/{id}` Printful API
- Telegram message with: order ID, total amount, item breakdown, which rule triggered, cancel confirmation
- Log to `hobson.order_events`

**On normal order (within limits)**:
- Telegram message: "New order #X: [items], total $Y"
- Log to `hobson.order_events`

**On errors (API failure, parse error, etc.)**:
- Telegram alert with error details
- Log raw webhook payload for debugging

## Database Schema

```sql
CREATE TABLE hobson.order_events (
    id SERIAL PRIMARY KEY,
    printful_order_id BIGINT NOT NULL,
    event_type TEXT NOT NULL,  -- 'order_received', 'order_cancelled', 'error'
    order_total NUMERIC(10,2),
    item_count INTEGER,
    rule_violated TEXT,        -- NULL if passed, 'max_total' or 'max_item_qty' if failed
    raw_payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(printful_order_id, event_type)
);
```

## Configuration

Environment variables on CT 255:

```
ORDER_MAX_TOTAL=50.00
ORDER_MAX_ITEM_QTY=3
PRINTFUL_API_KEY=<from Bitwarden>
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

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Printful retries webhook | Idempotent: check if order_id already processed |
| Order Guard is down | Webhooks fail, Printful retries. If still down after retries, order proceeds unchecked. Add Uptime Kuma monitor. |
| Printful API cancel fails | Telegram alert with order details for manual cancellation |
| Multiple small orders to circumvent limit | Not addressed in v1. Can add rolling 24-hour per-email limits later. |
| Hobson down, Order Guard up | Independent services, no dependency |

## Not In Scope

- Custom checkout/cart (over-engineered for current stage)
- Per-customer rolling limits (v2 if needed)
- Payment processing (Printful handles this)
- Refund handling (Printful handles this after cancellation)

## Risk Assessment

**Residual risk**: If Order Guard is down and Printful exhausts retries, a fraudulent order could proceed. Mitigation: Uptime Kuma monitoring with Telegram alerts on service downtime.

**Cancellation timing**: Printful orders sit in "Waiting for fulfillment" for hours before production starts. The webhook fires immediately on order creation. Auto-cancel happens within seconds. Production cost exposure is near-zero for detected orders.
