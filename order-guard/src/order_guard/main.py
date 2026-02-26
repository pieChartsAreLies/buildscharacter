"""Order Guard: Printful webhook receiver with fail-closed order confirmation."""
import hashlib
import hmac
import json
import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Request, Response

from order_guard import db, notify, printful
from order_guard.config import settings
from order_guard.rules import evaluate_order

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s"
)
logger = logging.getLogger("order_guard")

# Simple in-memory rate limiter
_request_times: list[float] = []
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 10


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Order Guard starting on port %s", settings.order_guard_port)
    yield
    logger.info("Order Guard shutting down")


app = FastAPI(title="Order Guard", version="0.1.0", lifespan=lifespan)


def _verify_signature(body: bytes, signature: str | None) -> bool:
    """Verify Printful HMAC signature."""
    if not signature or not settings.printful_webhook_secret:
        return False
    expected = hmac.new(
        settings.printful_webhook_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _check_rate_limit() -> bool:
    """Returns True if request is within rate limit."""
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW
    while _request_times and _request_times[0] < cutoff:
        _request_times.pop(0)
    if len(_request_times) >= RATE_LIMIT_MAX:
        return False
    _request_times.append(now)
    return True


def _extract_order_data(payload: dict) -> dict:
    """Extract order details from webhook payload."""
    order = payload.get("data", {}).get("order", {})
    costs = order.get("costs", {})
    retail_costs = order.get("retail_costs", {})
    items = order.get("items", [])

    return {
        "order_id": order.get("id"),
        "status": order.get("status"),
        "production_cost": float(costs.get("total", 0)),
        "retail_total": float(retail_costs.get("total", 0)),
        "items": [
            {
                "name": i.get("name", "Unknown"),
                "quantity": i.get("quantity", 1),
            }
            for i in items
        ],
        "item_count": sum(i.get("quantity", 1) for i in items),
    }


def _process_order(payload: dict):
    """Background task: evaluate order and confirm or hold."""
    try:
        order_data = _extract_order_data(payload)
        order_id = order_data["order_id"]

        if not order_id:
            logger.error("No order ID in payload")
            return

        # Get velocity count
        recent_count = db.get_recent_confirmed_count(hours=1)

        # Evaluate rules
        result = evaluate_order(
            production_cost=order_data["production_cost"],
            items=order_data["items"],
            recent_order_count=recent_count,
            max_production_cost=settings.order_max_production_cost,
            max_item_qty=settings.order_max_item_qty,
            max_hourly_velocity=settings.order_max_hourly_velocity,
        )

        if result.passed:
            # Check order status before confirming (idempotency at Printful level)
            existing = printful.get_order(order_id)
            if existing and existing.get("status") not in ("draft", "pending"):
                logger.info(
                    "Order %s already in status '%s', skipping confirm",
                    order_id,
                    existing.get("status"),
                )
                return

            # Confirm the order
            confirmed = printful.confirm_order(order_id)
            event_type = "order_confirmed" if confirmed else "error"

            db.log_event(
                printful_order_id=order_id,
                event_type=event_type,
                production_cost=order_data["production_cost"],
                retail_total=order_data["retail_total"],
                item_count=order_data["item_count"],
                raw_payload=payload,
            )

            if confirmed:
                msg = notify.format_confirmed_message(
                    order_id=order_id,
                    production_cost=order_data["production_cost"],
                    retail_total=order_data["retail_total"],
                    items=order_data["items"],
                )
            else:
                msg = notify.format_error_message(
                    order_id=order_id,
                    error="Failed to confirm order via Printful API",
                )
            notify.send_telegram(msg)

        else:
            # Hold the order (leave as draft)
            db.log_event(
                printful_order_id=order_id,
                event_type="order_held",
                production_cost=order_data["production_cost"],
                retail_total=order_data["retail_total"],
                item_count=order_data["item_count"],
                rule_violated=result.violated_rule,
                raw_payload=payload,
            )

            msg = notify.format_held_message(
                order_id=order_id,
                production_cost=order_data["production_cost"],
                retail_total=order_data["retail_total"],
                items=order_data["items"],
                rule_violated=result.violated_rule,
                reason=result.reason,
            )
            notify.send_telegram(msg)

    except Exception as e:
        logger.exception("Error processing order webhook")
        order_id = payload.get("data", {}).get("order", {}).get("id", "unknown")
        db.log_event(
            printful_order_id=int(order_id) if str(order_id).isdigit() else 0,
            event_type="error",
            raw_payload=payload,
            rule_violated=str(e),
        )
        notify.send_telegram(
            notify.format_error_message(order_id=order_id, error=str(e))
        )


@app.post("/printful/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    signature = request.headers.get("X-Printful-Signature")

    # Verify HMAC signature
    if not _verify_signature(body, signature):
        return Response(status_code=401, content="Invalid signature")

    # Rate limit
    if not _check_rate_limit():
        return Response(status_code=429, content="Rate limited")

    # Parse payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return Response(status_code=400, content="Invalid JSON")

    # Only process order_created events
    event_type = payload.get("type", "")
    if event_type != "order_created":
        logger.info("Ignoring webhook event type: %s", event_type)
        return {"status": "ignored", "reason": f"event type '{event_type}' not handled"}

    # Process in background
    background_tasks.add_task(_process_order, payload)

    return {"status": "received"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "order-guard", "version": "0.1.0"}


def main():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.order_guard_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
