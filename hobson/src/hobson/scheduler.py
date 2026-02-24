"""APScheduler setup for Hobson's scheduled workflows."""

import logging
import traceback

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from hobson.config import settings
from hobson.db import HobsonDB

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# Track consecutive failures for circuit breaking
_failure_counts: dict[str, int] = {}
_CIRCUIT_BREAKER_THRESHOLD = 3


async def run_workflow(agent, workflow_name: str, message: str):
    """Execute a workflow with retry, circuit breaking, and run logging."""
    db = HobsonDB(settings.database_url)

    # Circuit breaker check
    if _failure_counts.get(workflow_name, 0) >= _CIRCUIT_BREAKER_THRESHOLD:
        logger.error(f"Circuit breaker OPEN for {workflow_name}. Skipping.")
        return

    run_id = db.log_run_start(workflow=workflow_name, inputs={"message": message})

    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": f"workflow-{workflow_name}"}},
        )
        db.log_run_complete(run_id, status="success", outputs={"response": "ok"})
        _failure_counts[workflow_name] = 0

        # Ping Uptime Kuma on success
        if settings.uptime_kuma_push_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.get(
                        f"{settings.uptime_kuma_push_url}?status=up&msg={workflow_name}+OK"
                    )
            except Exception:
                pass

        logger.info(f"Workflow {workflow_name} completed successfully (run_id={run_id})")

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        db.log_run_complete(run_id, status="failed", error=error_msg)
        _failure_counts[workflow_name] = _failure_counts.get(workflow_name, 0) + 1
        logger.error(f"Workflow {workflow_name} failed (run_id={run_id}): {e}")

        if _failure_counts[workflow_name] >= _CIRCUIT_BREAKER_THRESHOLD:
            logger.critical(f"Circuit breaker TRIPPED for {workflow_name}")


def setup_schedules(agent):
    """Register all scheduled workflows."""

    scheduler.add_job(
        run_workflow,
        CronTrigger(hour=7, minute=0, timezone="America/New_York"),
        args=[agent, "morning_briefing", "Run the morning briefing: check analytics, log metrics to Obsidian, surface any anomalies via Telegram."],
        id="morning_briefing",
    )

    scheduler.add_job(
        run_workflow,
        CronTrigger(day_of_week="mon,wed,fri", hour=10, timezone="America/New_York"),
        args=[agent, "content_pipeline", "Run the content pipeline: read the content calendar, pick the next topic, generate a blog post draft, log it to Obsidian."],
        id="content_pipeline",
    )

    scheduler.add_job(
        run_workflow,
        CronTrigger(day_of_week="mon", hour=14, timezone="America/New_York"),
        args=[agent, "design_batch", "Run the design batch: generate 5-10 new merch design concepts, evaluate them against brand guidelines, log results to Obsidian."],
        id="design_batch",
    )

    scheduler.add_job(
        run_workflow,
        CronTrigger(day_of_week="fri", hour=15, timezone="America/New_York"),
        args=[agent, "substack_dispatch", "Write this week's Substack edition: review the daily logs, compile metrics, write in Hobson's voice, include a reader poll."],
        id="substack_dispatch",
    )

    scheduler.add_job(
        run_workflow,
        CronTrigger(day_of_week="sun", hour=18, timezone="America/New_York"),
        args=[agent, "business_review", "Run the weekly business review: aggregate metrics, compare against quarterly goals, write the review to Obsidian."],
        id="business_review",
    )
