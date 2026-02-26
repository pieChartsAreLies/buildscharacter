"""Telegram notification client for order events."""
import logging

import httpx

from order_guard.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"


def format_confirmed_message(
    order_id: int,
    production_cost: float,
    retail_total: float,
    items: list[dict],
) -> str:
    item_lines = "\n".join(
        f"  - {i.get('name', 'Unknown')} x{i.get('quantity', 1)}"
        for i in items
    )
    return (
        f"*Order Confirmed* `#{order_id}`\n\n"
        f"*Your cost:* ${production_cost:.2f}\n"
        f"*Retail total:* ${retail_total:.2f}\n"
        f"*Items:*\n{item_lines}"
    )


def format_held_message(
    order_id: int,
    production_cost: float,
    retail_total: float,
    items: list[dict],
    rule_violated: str,
    reason: str,
) -> str:
    item_lines = "\n".join(
        f"  - {i.get('name', 'Unknown')} x{i.get('quantity', 1)}"
        for i in items
    )
    return (
        f"*Order Held* `#{order_id}`\n\n"
        f"*Rule violated:* `{rule_violated}`\n"
        f"*Reason:* {reason}\n"
        f"*Your cost:* ${production_cost:.2f}\n"
        f"*Retail total:* ${retail_total:.2f}\n"
        f"*Items:*\n{item_lines}\n\n"
        f"[Review in Printful](https://www.printful.com/dashboard/default/orders)"
    )


def format_error_message(order_id: int, error: str) -> str:
    return (
        f"*Order Guard Error* `#{order_id}`\n\n"
        f"*Error:* {error}\n\n"
        f"Order remains as draft. Check Printful dashboard."
    )


def send_telegram(text: str) -> bool:
    """Send a message via Telegram Bot API. Returns True on success."""
    url = f"{TELEGRAM_API}/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return True
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error("Telegram send failed: %s", e)
        # Fall back to plain text if markdown fails
        try:
            payload["parse_mode"] = None
            with httpx.Client(timeout=10) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                return True
        except Exception:
            logger.error("Telegram send failed (plain text fallback): %s", e)
            return False
