"""PostgreSQL client for Hobson state management."""

import uuid
from datetime import date
from decimal import Decimal

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json


class HobsonDB:
    def __init__(self, database_url: str):
        self.database_url = database_url

    def _conn(self):
        return psycopg.connect(self.database_url, row_factory=dict_row)

    def log_run_start(self, workflow: str, inputs: dict, llm_provider: str | None = None) -> str:
        run_id = str(uuid.uuid4())
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.run_log (run_id, workflow, inputs, llm_provider, status)
                   VALUES (%s, %s, %s, %s, 'running')""",
                (run_id, workflow, Json(inputs), llm_provider),
            )
        return run_id

    def log_run_complete(
        self, run_id: str, status: str, outputs: dict | None = None, error: str | None = None
    ):
        with self._conn() as conn:
            conn.execute(
                """UPDATE hobson.run_log
                   SET status = %s, completed_at = NOW(), outputs = %s, error = %s
                   WHERE run_id = %s""",
                (status, Json(outputs or {}), error, run_id),
            )

    def get_run(self, run_id: str) -> dict | None:
        with self._conn() as conn:
            return conn.execute(
                "SELECT * FROM hobson.run_log WHERE run_id = %s", (run_id,)
            ).fetchone()

    def log_decision(
        self,
        decision: str,
        reasoning: str,
        category: str | None = None,
        outcome: str | None = None,
    ):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.decisions (decision, reasoning, category, outcome)
                   VALUES (%s, %s, %s, %s)""",
                (decision, reasoning, category, outcome),
            )

    def log_cost(self, run_id: str, provider: str, action: str, estimated_cost: float):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.cost_log (run_id, provider, action, estimated_cost)
                   VALUES (%s, %s, %s, %s)""",
                (run_id, provider, action, estimated_cost),
            )

    def get_daily_cost_total(self, target_date: date | None = None) -> float:
        target_date = target_date or date.today()
        with self._conn() as conn:
            result = conn.execute(
                """SELECT COALESCE(SUM(estimated_cost), 0) as total
                   FROM hobson.cost_log WHERE created_at::date = %s""",
                (target_date,),
            ).fetchone()
            return float(result["total"])

    def get_monthly_cost_total(self) -> float:
        with self._conn() as conn:
            result = conn.execute(
                """SELECT COALESCE(SUM(estimated_cost), 0) as total
                   FROM hobson.cost_log
                   WHERE date_trunc('month', created_at) = date_trunc('month', NOW())""",
            ).fetchone()
            return float(result["total"])

    def log_metric(self, metric_type: str, data: dict, target_date: date | None = None):
        target_date = target_date or date.today()
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.metrics (date, metric_type, data)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (date, metric_type) DO UPDATE SET data = EXCLUDED.data""",
                (target_date, metric_type, Json(data)),
            )

    def create_task(
        self,
        title: str,
        description: str | None = None,
        priority: str = "medium",
        due_date: date | None = None,
        goal_id: str | None = None,
    ) -> str:
        task_id = str(uuid.uuid4())
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.tasks (id, title, description, priority, due_date, goal_id)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (task_id, title, description, priority, due_date, goal_id),
            )
        return task_id

    def update_task_status(self, task_id: str, status: str):
        with self._conn() as conn:
            conn.execute(
                "UPDATE hobson.tasks SET status = %s, updated_at = NOW() WHERE id = %s",
                (status, task_id),
            )

    # -- Message history --

    def store_message(self, chat_id: str, sender_name: str, content: str, is_from_hobson: bool = False):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.messages (chat_id, sender_name, content, is_from_hobson)
                   VALUES (%s, %s, %s, %s)""",
                (chat_id, sender_name, content, is_from_hobson),
            )

    def get_recent_messages(self, chat_id: str, limit: int = 20) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT sender_name, content, is_from_hobson, timestamp
                   FROM hobson.messages
                   WHERE chat_id = %s
                   ORDER BY timestamp DESC
                   LIMIT %s""",
                (chat_id, limit),
            ).fetchall()
            return list(reversed(rows))  # chronological order

    # -- Approvals --

    def create_approval(self, request_id: str, action: str, reasoning: str, estimated_cost: float = 0):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.approvals (request_id, action, reasoning, estimated_cost)
                   VALUES (%s, %s, %s, %s)""",
                (request_id, action, reasoning, estimated_cost),
            )

    def resolve_approval(self, request_id: str, approved: bool):
        status = "approved" if approved else "denied"
        with self._conn() as conn:
            conn.execute(
                """UPDATE hobson.approvals
                   SET status = %s, resolved_at = NOW()
                   WHERE request_id = %s""",
                (status, request_id),
            )

    def get_approval_status(self, request_id: str) -> str | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT status FROM hobson.approvals WHERE request_id = %s",
                (request_id,),
            ).fetchone()
            return row["status"] if row else None

    def get_approval_record(self, request_id: str) -> dict | None:
        with self._conn() as conn:
            return conn.execute(
                "SELECT * FROM hobson.approvals WHERE request_id = %s",
                (request_id,),
            ).fetchone()

    def get_pending_approvals(self) -> list[dict]:
        """Get all unresolved approval requests."""
        with self._conn() as conn:
            return conn.execute(
                "SELECT request_id, action, reasoning, estimated_cost, created_at "
                "FROM hobson.approvals WHERE resolved_at IS NULL "
                "ORDER BY created_at DESC"
            ).fetchall()

    # -- Design generations --

    def log_design_generation(
        self,
        concept_name: str,
        generation_prompt: str,
        model_version: str = "imagen-4.0-generate-001",
        image_url: str | None = None,
        r2_filename: str | None = None,
        product_type: str | None = None,
        generation_status: str = "success",
        status_reason: str | None = None,
        image_width: int | None = None,
        image_height: int | None = None,
    ) -> int:
        with self._conn() as conn:
            row = conn.execute(
                """INSERT INTO hobson.design_generations
                   (concept_name, generation_prompt, model_version, image_url,
                    r2_filename, product_type, generation_status, status_reason,
                    image_width, image_height)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id""",
                (
                    concept_name, generation_prompt, model_version, image_url,
                    r2_filename, product_type, generation_status, status_reason,
                    image_width, image_height,
                ),
            ).fetchone()
            return row["id"]
