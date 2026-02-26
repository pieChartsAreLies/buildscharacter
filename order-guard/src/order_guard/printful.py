"""Printful API client for order confirmation."""
import logging

import httpx

from order_guard.config import settings

logger = logging.getLogger(__name__)

API_BASE = "https://api.printful.com"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.printful_api_key}"}


def confirm_order(order_id: int) -> bool:
    """Confirm a draft order for fulfillment. Returns True on success."""
    url = f"{API_BASE}/orders/{order_id}/confirm"
    try:
        with httpx.Client(headers=_headers(), timeout=30) as client:
            resp = client.post(url)
            resp.raise_for_status()
            logger.info("Confirmed order %s", order_id)
            return True
    except httpx.HTTPStatusError as e:
        logger.error("Failed to confirm order %s: %s %s", order_id, e.response.status_code, e.response.text)
        return False
    except httpx.RequestError as e:
        logger.error("Request error confirming order %s: %s", order_id, e)
        return False


def get_order(order_id: int) -> dict | None:
    """Fetch full order details. Returns order dict or None on failure."""
    url = f"{API_BASE}/orders/{order_id}"
    try:
        with httpx.Client(headers=_headers(), timeout=30) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json().get("result", {})
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error("Failed to fetch order %s: %s", order_id, e)
        return None
