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
