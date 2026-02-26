"""Tests for webhook endpoint."""
import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient


# Minimal valid Printful webhook payload
def _make_payload(
    order_id: int = 12345,
    status: str = "draft",
    total_cost: float = 18.50,
    retail_total: float = 34.99,
    items: list | None = None,
) -> dict:
    if items is None:
        items = [
            {
                "name": "Build Character Sticker",
                "quantity": 2,
                "retail_price": "17.49",
            }
        ]
    return {
        "type": "order_created",
        "data": {
            "order": {
                "id": order_id,
                "status": status,
                "costs": {
                    "subtotal": str(total_cost),
                    "shipping": "0.00",
                    "total": str(total_cost),
                },
                "retail_costs": {
                    "subtotal": str(retail_total),
                    "shipping": "5.00",
                    "total": str(retail_total),
                },
                "items": items,
            }
        },
    }


def _sign_payload(payload: dict, secret: str) -> str:
    """Sign payload using the same serialization that TestClient uses.

    TestClient uses httpx which serializes JSON with compact separators
    (',' and ':' -- no spaces), so we must match that exactly.
    """
    body = json.dumps(payload, separators=(",", ":"))
    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


@pytest.fixture
def client(monkeypatch):
    """TestClient with mocked config and DB."""
    monkeypatch.setenv("PRINTFUL_WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("PRINTFUL_API_KEY", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-chat")
    monkeypatch.setenv("DATABASE_URL", "postgresql://fake:fake@localhost/fake")

    # Reimport to pick up env overrides
    import importlib
    import order_guard.config

    importlib.reload(order_guard.config)

    # Mock DB and external calls
    import order_guard.db as db_mod
    import order_guard.notify as notify_mod
    import order_guard.printful as printful_mod

    monkeypatch.setattr(db_mod, "log_event", lambda **kwargs: True)
    monkeypatch.setattr(db_mod, "get_recent_confirmed_count", lambda hours=1: 0)
    monkeypatch.setattr(printful_mod, "confirm_order", lambda order_id: True)
    monkeypatch.setattr(printful_mod, "get_order", lambda order_id: {"status": "draft"})
    monkeypatch.setattr(notify_mod, "send_telegram", lambda text: True)

    from order_guard.main import app

    return TestClient(app)


class TestWebhookSecurity:
    def test_missing_signature_returns_401(self, client):
        resp = client.post("/printful/webhook", json=_make_payload())
        assert resp.status_code == 401

    def test_invalid_signature_returns_401(self, client):
        resp = client.post(
            "/printful/webhook",
            json=_make_payload(),
            headers={"X-Printful-Signature": "invalid"},
        )
        assert resp.status_code == 401

    def test_valid_signature_returns_200(self, client):
        payload = _make_payload()
        sig = _sign_payload(payload, "test-secret")
        resp = client.post(
            "/printful/webhook",
            json=payload,
            headers={"X-Printful-Signature": sig},
        )
        assert resp.status_code == 200

    def test_get_request_returns_405(self, client):
        resp = client.get("/printful/webhook")
        assert resp.status_code == 405


class TestWebhookProcessing:
    def test_returns_200_immediately(self, client):
        """Webhook should return 200 before processing completes."""
        payload = _make_payload()
        sig = _sign_payload(payload, "test-secret")
        resp = client.post(
            "/printful/webhook",
            json=payload,
            headers={"X-Printful-Signature": sig},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "received"


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
