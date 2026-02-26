# Order Guard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a fail-closed webhook service that receives Printful order events, evaluates orders against configurable limits (production cost, item quantity, hourly velocity), and auto-confirms safe orders while holding suspicious ones as drafts.

**Architecture:** Standalone FastAPI service on CT 255 (separate from Hobson), receiving Printful webhooks via Cloudflare Tunnel. Orders default to draft status in Printful; the service explicitly confirms orders that pass all rules. If the service is down, orders stay as drafts (fail-closed). Telegram notifications for all order events.

**Tech Stack:** Python 3.11, FastAPI, uvicorn, httpx (Printful API + Telegram Bot API), psycopg (PostgreSQL), pydantic-settings, pytest

---

## Project Structure

```
order-guard/
├── src/order_guard/
│   ├── __init__.py
│   ├── main.py         # FastAPI app + uvicorn entry point
│   ├── config.py        # pydantic-settings
│   ├── rules.py         # Order evaluation logic (pure functions)
│   ├── printful.py      # Printful API client (confirm order)
│   ├── notify.py        # Telegram notifications via Bot API
│   └── db.py            # PostgreSQL logging
├── tests/
│   ├── test_rules.py
│   ├── test_webhook.py
│   └── test_notify.py
├── deploy/
│   └── order-guard.service
├── pyproject.toml
└── .env.example
```

Lives at `/Users/llama/Development/builds-character/order-guard/` alongside `hobson/` and `site/`.

---

### Task 1: Database Migration

**Files:**
- Create: `hobson/sql/003_order_events.sql`

**Step 1: Write the migration SQL**

```sql
-- Order Guard: order event audit log
CREATE TABLE IF NOT EXISTS hobson.order_events (
    id SERIAL PRIMARY KEY,
    printful_order_id BIGINT NOT NULL,
    event_type TEXT NOT NULL,
    production_cost NUMERIC(10,2),
    retail_total NUMERIC(10,2),
    item_count INTEGER,
    rule_violated TEXT,
    raw_payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(printful_order_id, event_type)
);

CREATE INDEX IF NOT EXISTS idx_order_events_created_at
    ON hobson.order_events(created_at);
```

Save to `hobson/sql/003_order_events.sql`.

**Step 2: Apply migration on CT 201**

Run from Proxmox host Freya:
```bash
ssh root@192.168.2.13
pct exec 201 -- psql -U hobson -d project_data -f -
```

Paste the SQL and verify with:
```bash
pct exec 201 -- psql -U hobson -d project_data -c "\d hobson.order_events"
```

Expected: table with 9 columns, unique constraint on (printful_order_id, event_type).

**Step 3: Commit**

```bash
git add hobson/sql/003_order_events.sql
git commit -m "feat: add order_events table for Order Guard audit log"
```

---

### Task 2: Project Scaffold + Config

**Files:**
- Create: `order-guard/pyproject.toml`
- Create: `order-guard/src/order_guard/__init__.py`
- Create: `order-guard/src/order_guard/config.py`
- Create: `order-guard/.env.example`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "order-guard"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn>=0.30",
    "httpx>=0.27",
    "psycopg[binary]>=3.2",
    "pydantic-settings>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.24",
    "pytest-httpx>=0.30",
    "ruff>=0.5",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
pythonpath = ["src"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends._legacy:_Backend"
```

**Step 2: Create config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Printful
    printful_api_key: str = ""
    printful_webhook_secret: str = ""

    # Telegram (uses Bob's bot)
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # PostgreSQL (same DB as Hobson)
    database_url: str = "postgresql://hobson:password@192.168.2.67:5432/project_data"

    # Order limits
    order_max_production_cost: float = 50.0
    order_max_item_qty: int = 3
    order_max_hourly_velocity: int = 5

    # Server
    order_guard_port: int = 8100

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

**Step 3: Create .env.example**

```
PRINTFUL_API_KEY=
PRINTFUL_WEBHOOK_SECRET=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DATABASE_URL=postgresql://hobson:PASSWORD@192.168.2.67:5432/project_data
ORDER_MAX_PRODUCTION_COST=50.00
ORDER_MAX_ITEM_QTY=3
ORDER_MAX_HOURLY_VELOCITY=5
ORDER_GUARD_PORT=8100
```

**Step 4: Create empty __init__.py**

```python
```

**Step 5: Commit**

```bash
git add order-guard/
git commit -m "feat: scaffold order-guard project with config"
```

---

### Task 3: Order Evaluation Rules (TDD)

**Files:**
- Create: `order-guard/src/order_guard/rules.py`
- Create: `order-guard/tests/test_rules.py`

**Step 1: Write failing tests for rules**

```python
"""Tests for order evaluation rules."""
from order_guard.rules import evaluate_order, RuleResult


class TestProductionCostRule:
    def test_under_limit_passes(self):
        result = evaluate_order(
            production_cost=25.00,
            items=[{"quantity": 1}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is True
        assert result.violated_rule is None

    def test_at_limit_passes(self):
        result = evaluate_order(
            production_cost=50.00,
            items=[{"quantity": 1}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is True

    def test_over_limit_fails(self):
        result = evaluate_order(
            production_cost=75.00,
            items=[{"quantity": 1}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is False
        assert result.violated_rule == "max_cost"
        assert "75.00" in result.reason


class TestItemQuantityRule:
    def test_within_limit_passes(self):
        result = evaluate_order(
            production_cost=10.00,
            items=[{"quantity": 2}, {"quantity": 3}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is True

    def test_over_limit_fails(self):
        result = evaluate_order(
            production_cost=10.00,
            items=[{"quantity": 5}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is False
        assert result.violated_rule == "max_item_qty"

    def test_multiple_items_one_over_fails(self):
        result = evaluate_order(
            production_cost=10.00,
            items=[{"quantity": 1}, {"quantity": 4}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is False
        assert result.violated_rule == "max_item_qty"


class TestVelocityRule:
    def test_under_velocity_passes(self):
        result = evaluate_order(
            production_cost=10.00,
            items=[{"quantity": 1}],
            recent_order_count=3,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is True

    def test_at_velocity_limit_fails(self):
        result = evaluate_order(
            production_cost=10.00,
            items=[{"quantity": 1}],
            recent_order_count=5,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.passed is False
        assert result.violated_rule == "velocity"


class TestRulePriority:
    """First failing rule is reported."""

    def test_cost_checked_before_quantity(self):
        result = evaluate_order(
            production_cost=100.00,
            items=[{"quantity": 10}],
            recent_order_count=0,
            max_production_cost=50.0,
            max_item_qty=3,
            max_hourly_velocity=5,
        )
        assert result.violated_rule == "max_cost"
```

Save to `order-guard/tests/test_rules.py`.

**Step 2: Run tests to verify they fail**

```bash
cd order-guard && python -m pytest tests/test_rules.py -v
```

Expected: FAIL (ModuleNotFoundError: order_guard.rules)

**Step 3: Write minimal implementation**

```python
"""Order evaluation rules. Pure functions, no I/O."""
from dataclasses import dataclass


@dataclass
class RuleResult:
    passed: bool
    violated_rule: str | None = None
    reason: str | None = None


def evaluate_order(
    production_cost: float,
    items: list[dict],
    recent_order_count: int,
    max_production_cost: float,
    max_item_qty: int,
    max_hourly_velocity: int,
) -> RuleResult:
    """Evaluate an order against all rules. Returns first violation or pass."""
    # Rule 1: production cost cap
    if production_cost > max_production_cost:
        return RuleResult(
            passed=False,
            violated_rule="max_cost",
            reason=f"Production cost ${production_cost:.2f} exceeds limit ${max_production_cost:.2f}",
        )

    # Rule 2: per-item quantity cap
    for item in items:
        if item.get("quantity", 0) > max_item_qty:
            return RuleResult(
                passed=False,
                violated_rule="max_item_qty",
                reason=f"Item quantity {item['quantity']} exceeds limit {max_item_qty}",
            )

    # Rule 3: hourly velocity cap
    if recent_order_count >= max_hourly_velocity:
        return RuleResult(
            passed=False,
            violated_rule="velocity",
            reason=f"Hourly order count {recent_order_count} exceeds limit {max_hourly_velocity}",
        )

    return RuleResult(passed=True)
```

Save to `order-guard/src/order_guard/rules.py`.

**Step 4: Run tests to verify they pass**

```bash
cd order-guard && python -m pytest tests/test_rules.py -v
```

Expected: all 8 tests PASS.

**Step 5: Commit**

```bash
git add order-guard/src/order_guard/rules.py order-guard/tests/test_rules.py
git commit -m "feat: add order evaluation rules with tests"
```

---

### Task 4: Database Client

**Files:**
- Create: `order-guard/src/order_guard/db.py`

**Step 1: Write the database client**

```python
"""PostgreSQL client for order event logging."""
import logging

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from order_guard.config import settings

logger = logging.getLogger(__name__)


def _conn():
    return psycopg.connect(settings.database_url, row_factory=dict_row)


def log_event(
    printful_order_id: int,
    event_type: str,
    production_cost: float | None = None,
    retail_total: float | None = None,
    item_count: int | None = None,
    rule_violated: str | None = None,
    raw_payload: dict | None = None,
) -> bool:
    """Log an order event. Returns True if inserted, False if duplicate."""
    with _conn() as conn:
        result = conn.execute(
            """INSERT INTO hobson.order_events
               (printful_order_id, event_type, production_cost, retail_total,
                item_count, rule_violated, raw_payload)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (printful_order_id, event_type) DO NOTHING""",
            (
                printful_order_id,
                event_type,
                production_cost,
                retail_total,
                item_count,
                rule_violated,
                Json(raw_payload) if raw_payload else None,
            ),
        )
        return result.rowcount > 0


def get_recent_confirmed_count(hours: int = 1) -> int:
    """Count orders confirmed in the last N hours (for velocity check)."""
    with _conn() as conn:
        row = conn.execute(
            """SELECT COUNT(*) AS cnt FROM hobson.order_events
               WHERE event_type = 'order_confirmed'
               AND created_at > NOW() - INTERVAL '%s hours'""",
            (hours,),
        ).fetchone()
        return row["cnt"] if row else 0
```

Save to `order-guard/src/order_guard/db.py`.

**Step 2: Commit**

```bash
git add order-guard/src/order_guard/db.py
git commit -m "feat: add order event database client"
```

---

### Task 5: Printful API Client

**Files:**
- Create: `order-guard/src/order_guard/printful.py`

**Step 1: Write the Printful client**

```python
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
```

Save to `order-guard/src/order_guard/printful.py`.

**Step 2: Commit**

```bash
git add order-guard/src/order_guard/printful.py
git commit -m "feat: add Printful API client for order confirmation"
```

---

### Task 6: Telegram Notification Client

**Files:**
- Create: `order-guard/src/order_guard/notify.py`
- Create: `order-guard/tests/test_notify.py`

**Step 1: Write failing test for message formatting**

```python
"""Tests for notification message formatting."""
from order_guard.notify import format_confirmed_message, format_held_message, format_error_message


class TestFormatConfirmedMessage:
    def test_basic_confirmed(self):
        msg = format_confirmed_message(
            order_id=12345,
            production_cost=18.50,
            retail_total=34.99,
            items=[{"name": "Build Character Sticker", "quantity": 2}],
        )
        assert "12345" in msg
        assert "18.50" in msg
        assert "34.99" in msg
        assert "Sticker" in msg
        assert "Confirmed" in msg


class TestFormatHeldMessage:
    def test_cost_violation(self):
        msg = format_held_message(
            order_id=12345,
            production_cost=75.00,
            retail_total=120.00,
            items=[{"name": "Hoodie", "quantity": 1}],
            rule_violated="max_cost",
            reason="Production cost $75.00 exceeds limit $50.00",
        )
        assert "12345" in msg
        assert "HELD" in msg or "Held" in msg
        assert "75.00" in msg
        assert "max_cost" in msg


class TestFormatErrorMessage:
    def test_error_message(self):
        msg = format_error_message(
            order_id=12345,
            error="Connection refused",
        )
        assert "12345" in msg
        assert "Error" in msg or "ERROR" in msg
        assert "Connection refused" in msg
```

Save to `order-guard/tests/test_notify.py`.

**Step 2: Run tests to verify they fail**

```bash
cd order-guard && python -m pytest tests/test_notify.py -v
```

Expected: FAIL (ModuleNotFoundError)

**Step 3: Write implementation**

```python
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
```

Save to `order-guard/src/order_guard/notify.py`.

**Step 4: Run tests to verify they pass**

```bash
cd order-guard && python -m pytest tests/test_notify.py -v
```

Expected: all 3 tests PASS (format functions are pure, no network).

**Step 5: Commit**

```bash
git add order-guard/src/order_guard/notify.py order-guard/tests/test_notify.py
git commit -m "feat: add Telegram notification client with message formatting"
```

---

### Task 7: Webhook Endpoint (TDD)

**Files:**
- Create: `order-guard/src/order_guard/main.py`
- Create: `order-guard/tests/test_webhook.py`

**Step 1: Write failing tests for the webhook endpoint**

Note: These tests use pytest-httpx to mock outbound HTTP calls and FastAPI's TestClient. They test the full request flow without hitting real services.

```python
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
    body = json.dumps(payload, separators=(",", ":"))
    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


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
    import order_guard.printful as printful_mod
    import order_guard.notify as notify_mod

    monkeypatch.setattr(db_mod, "log_event", lambda **kwargs: True)
    monkeypatch.setattr(db_mod, "get_recent_confirmed_count", lambda hours=1: 0)
    monkeypatch.setattr(printful_mod, "confirm_order", lambda order_id: True)
    monkeypatch.setattr(notify_mod, "send_telegram", lambda text: True)

    from order_guard.main import app
    return TestClient(app)
```

Save to `order-guard/tests/test_webhook.py`.

**Step 2: Run tests to verify they fail**

```bash
cd order-guard && python -m pytest tests/test_webhook.py -v
```

Expected: FAIL (ModuleNotFoundError: order_guard.main)

**Step 3: Write the FastAPI application**

```python
"""Order Guard: Printful webhook receiver with fail-closed order confirmation."""
import hashlib
import hmac
import json
import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Header, Request, Response

from order_guard.config import settings
from order_guard import db, notify, printful
from order_guard.rules import evaluate_order

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
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
    # Remove old entries
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
                logger.info("Order %s already in status '%s', skipping confirm", order_id, existing.get("status"))
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
```

Save to `order-guard/src/order_guard/main.py`.

**Step 4: Run tests to verify they pass**

```bash
cd order-guard && python -m pytest tests/test_webhook.py -v
```

Expected: all 5 tests PASS.

**Step 5: Run all tests together**

```bash
cd order-guard && python -m pytest -v
```

Expected: all 16 tests PASS (8 rules + 3 notify + 5 webhook).

**Step 6: Commit**

```bash
git add order-guard/src/order_guard/main.py order-guard/tests/test_webhook.py
git commit -m "feat: add FastAPI webhook endpoint with HMAC auth and background processing"
```

---

### Task 8: Systemd Service File

**Files:**
- Create: `order-guard/deploy/order-guard.service`

**Step 1: Write the service file**

```ini
[Unit]
Description=Order Guard - Printful webhook order limiter
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/builds-character/order-guard
Environment=PATH=/root/builds-character/order-guard/.venv/bin:/usr/local/bin:/usr/bin
ExecStart=/root/builds-character/order-guard/.venv/bin/python -m order_guard.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save to `order-guard/deploy/order-guard.service`.

**Step 2: Commit**

```bash
git add order-guard/deploy/order-guard.service
git commit -m "feat: add systemd service for Order Guard"
```

---

### Task 9: Deploy to CT 255

**Prerequisite:** Push code to GitHub first.

**Step 1: Push to remote**

```bash
git push origin master
```

**Step 2: Pull code on CT 255**

From Proxmox host Loki:
```bash
ssh root@192.168.2.16
pct exec 255 -- bash -c 'cd /root/builds-character && git pull'
```

**Step 3: Create venv and install**

```bash
pct exec 255 -- bash -c 'cd /root/builds-character/order-guard && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"'
```

**Step 4: Create .env file**

```bash
pct exec 255 -- bash -c 'cp /root/builds-character/order-guard/.env.example /root/builds-character/order-guard/.env'
```

Then edit `.env` on CT 255 with real values from Bitwarden:
- PRINTFUL_API_KEY (same as Hobson's)
- PRINTFUL_WEBHOOK_SECRET (generate new, save to Bitwarden)
- TELEGRAM_BOT_TOKEN (Bob's token, same as Hobson's)
- TELEGRAM_CHAT_ID (your chat ID)
- DATABASE_URL (hobson user, same connection string)

**Step 5: Run tests on CT 255**

```bash
pct exec 255 -- bash -c 'cd /root/builds-character/order-guard && .venv/bin/python -m pytest -v'
```

Expected: all tests PASS.

**Step 6: Install and start systemd service**

```bash
pct exec 255 -- bash -c 'cp /root/builds-character/order-guard/deploy/order-guard.service /etc/systemd/system/ && systemctl daemon-reload && systemctl enable order-guard && systemctl start order-guard'
```

**Step 7: Verify service is running**

```bash
pct exec 255 -- systemctl status order-guard
pct exec 255 -- curl -s http://localhost:8100/health
```

Expected: service active, health endpoint returns `{"status": "ok"}`.

---

### Task 10: Cloudflare Tunnel Setup

**Step 1: Check if cloudflared exists on CT 255**

```bash
pct exec 255 -- which cloudflared
pct exec 255 -- systemctl list-units | grep cloudflared
```

**Step 2: Install cloudflared if needed**

If not installed:
```bash
pct exec 255 -- bash -c 'curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb && dpkg -i /tmp/cloudflared.deb'
```

**Step 3: Create or extend tunnel**

This step requires Cloudflare dashboard access. Either:
- Create a new tunnel via `cloudflared tunnel create order-guard`
- Or configure an existing tunnel to add a route

Add route for `webhooks.buildscharacter.com` pointing to `http://localhost:8100`.

**Step 4: Verify tunnel**

From any machine:
```bash
curl -s https://webhooks.buildscharacter.com/health
```

Expected: `{"status": "ok", "service": "order-guard"}`.

---

### Task 11: Printful Dashboard Configuration

**Step 1: Enable manual order approval**

In Printful Dashboard:
1. Go to Store Settings
2. Find order approval/confirmation settings
3. Enable "Manually approve all orders" or equivalent draft mode
4. Save

**Important:** Verify this setting exists. If Printful's hosted checkout (Quick Stores / printful.me) does not support draft mode, this is a blocker. Check Printful docs or contact support. The alternative is to use webhook-based cancellation (original v1 design) if draft mode isn't available for hosted stores.

**Step 2: Configure webhook**

In Printful Dashboard:
1. Go to Store Settings > Webhooks
2. Add webhook URL: `https://webhooks.buildscharacter.com/printful/webhook`
3. Set webhook secret (same value as PRINTFUL_WEBHOOK_SECRET in .env)
4. Subscribe to `order_created` event
5. Save

**Step 3: Verify webhook delivery**

Place a test order (use Printful's test mode if available) and verify:
- Order Guard receives the webhook (check logs: `journalctl -u order-guard -f`)
- Telegram notification is sent
- Event is logged in PostgreSQL

```bash
pct exec 201 -- psql -U hobson -d project_data -c "SELECT * FROM hobson.order_events ORDER BY created_at DESC LIMIT 5;"
```

---

### Task 12: Uptime Kuma Monitor

**Step 1: Add HTTP monitor**

On Uptime Kuma (CT 182, 192.168.2.182:3001):
1. Add new monitor
2. Type: HTTP
3. URL: `http://192.168.2.232:8100/health`
4. Interval: 60 seconds
5. Name: "Order Guard"
6. Set up Telegram notification on down

---

### Task 13: Documentation Updates

**Files:**
- Modify: `homelab-docs/docs/services/containers.md` (add Order Guard entry for CT 255)
- Modify: `homelab-docs/docs/operations/changelog.md` (add dated entry)

**Step 1: Update containers doc**

Add Order Guard as a service on CT 255 (alongside Hobson).

**Step 2: Update changelog**

```markdown
## 2026-02-26

- **Order Guard deployed** (CT 255): Fail-closed webhook service for Printful order limits.
  Confirms orders under $50 production cost / 3 items / 5/hour velocity. Orders exceeding
  limits held as drafts for manual review. CF Tunnel at webhooks.buildscharacter.com.
```

**Step 3: Commit and push**

```bash
cd /Users/llama/Development/homelab-docs
git add docs/services/containers.md docs/operations/changelog.md
git commit -m "docs: add Order Guard service to container docs and changelog"
git push origin main
```

---

## Verification Checklist

After all tasks are complete, verify end-to-end:

1. [ ] Order Guard service running on CT 255 (`systemctl status order-guard`)
2. [ ] Health endpoint reachable via CF Tunnel (`curl https://webhooks.buildscharacter.com/health`)
3. [ ] Printful webhook configured and delivering
4. [ ] Printful store set to manual approval / draft mode
5. [ ] Test order within limits: confirmed automatically, Telegram notification received
6. [ ] Test order over limits: held as draft, Telegram alert received
7. [ ] Uptime Kuma monitoring green
8. [ ] PostgreSQL events logged correctly
9. [ ] All tests passing (`pytest -v` in order-guard/)
10. [ ] Homelab docs updated and live on doc site

## Important Notes

- **HMAC verification**: Verify that Printful actually sends `X-Printful-Signature` headers with the webhook secret. If they use a different mechanism, adjust `_verify_signature()` accordingly. Check [Printful API docs](https://developers.printful.com/docs/) during implementation.
- **Draft mode availability**: Verify that Printful's hosted checkout (printful.me / Quick Stores) supports manual order approval. If not, fall back to the cancel-bad-orders approach (keep existing code but swap `confirm_order` for `cancel_order` and invert the rule logic).
- **Shared credentials**: Order Guard uses the same Printful API key, Telegram bot token, and PostgreSQL user as Hobson. No new credentials needed except the webhook secret.

## Adversarial Review Changes

After Gemini adversarial review, three improvements were incorporated:
1. **Event type filtering**: Webhook handler checks `type` field and only processes `order_created`, ignoring other event types
2. **Printful dashboard link**: Held-order Telegram notifications include a direct link to the Printful orders dashboard
3. **Order status check before confirming**: Calls `get_order()` to verify the order is still in draft/pending status before attempting to confirm, preventing double-confirmation on retries
