"""APScheduler setup for Hobson's scheduled workflows."""

import logging
import traceback

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from hobson.config import settings
from hobson.db import HobsonDB
from hobson.workflows.business_review import BUSINESS_REVIEW_PROMPT
from hobson.workflows.content_pipeline import CONTENT_PIPELINE_PROMPT
from hobson.workflows.bootstrap_diary import BOOTSTRAP_DIARY_PROMPT
from hobson.workflows.design_batch import DESIGN_BATCH_BOOTSTRAP_PROMPT, DESIGN_BATCH_PROMPT
from hobson.workflows.morning_briefing import MORNING_BRIEFING_PROMPT
from hobson.workflows.substack_dispatch import SUBSTACK_DISPATCH_PROMPT

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# Track consecutive failures for circuit breaking
_failure_counts: dict[str, int] = {}
_CIRCUIT_BREAKER_THRESHOLD = 3


# Map workflow names to their Uptime Kuma push URLs
_PUSH_URLS = {
    "morning_briefing": lambda: settings.uptime_kuma_push_morning_briefing,
    "content_pipeline": lambda: settings.uptime_kuma_push_content_pipeline,
    "design_batch": lambda: settings.uptime_kuma_push_design_batch,
    "substack_dispatch": lambda: settings.uptime_kuma_push_substack_dispatch,
    "business_review": lambda: settings.uptime_kuma_push_business_review,
}


async def run_workflow(agent, workflow_name: str, message: str):
    """Execute a workflow with retry, circuit breaking, and run logging."""
    db = HobsonDB(settings.database_url)

    # Circuit breaker check
    if _failure_counts.get(workflow_name, 0) >= _CIRCUIT_BREAKER_THRESHOLD:
        logger.error(f"Circuit breaker OPEN for {workflow_name}. Skipping.")
        return

    run_id = db.log_run_start(workflow=workflow_name, inputs={"message": message})

    try:
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": f"workflow-{workflow_name}"}},
        )
        db.log_run_complete(run_id, status="success", outputs={"response": "ok"})
        _failure_counts[workflow_name] = 0

        # Ping this workflow's Uptime Kuma push URL on success
        push_url = _PUSH_URLS.get(workflow_name, lambda: "")()
        if push_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.get(push_url)
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
    """Register all scheduled workflows. Cadence depends on bootstrap_mode."""

    # Morning briefing: always daily 7am ET
    scheduler.add_job(
        run_workflow,
        CronTrigger(hour=7, minute=0, timezone="America/New_York"),
        args=[agent, "morning_briefing", MORNING_BRIEFING_PROMPT],
        id="morning_briefing",
    )

    if settings.bootstrap_mode:
        # Content pipeline: 3x/day (8am, 1pm, 6pm ET)
        for hour, suffix in [(8, "am"), (13, "midday"), (18, "pm")]:
            scheduler.add_job(
                run_workflow,
                CronTrigger(hour=hour, minute=0, timezone="America/New_York"),
                args=[agent, "content_pipeline", CONTENT_PIPELINE_PROMPT],
                id=f"content_pipeline_{suffix}",
            )

        # Bootstrap diary: daily 9pm ET
        scheduler.add_job(
            run_workflow,
            CronTrigger(hour=21, minute=0, timezone="America/New_York"),
            args=[agent, "bootstrap_diary", BOOTSTRAP_DIARY_PROMPT],
            id="bootstrap_diary",
        )

        # Design batch: daily 2pm ET
        scheduler.add_job(
            run_workflow,
            CronTrigger(hour=14, minute=0, timezone="America/New_York"),
            args=[agent, "design_batch", DESIGN_BATCH_BOOTSTRAP_PROMPT],
            id="design_batch",
        )
    else:
        # Content pipeline: MWF 10am ET
        scheduler.add_job(
            run_workflow,
            CronTrigger(day_of_week="mon,wed,fri", hour=10, timezone="America/New_York"),
            args=[agent, "content_pipeline", CONTENT_PIPELINE_PROMPT],
            id="content_pipeline",
        )

        # Design batch: Monday 2pm ET
        scheduler.add_job(
            run_workflow,
            CronTrigger(day_of_week="mon", hour=14, timezone="America/New_York"),
            args=[agent, "design_batch", DESIGN_BATCH_PROMPT],
            id="design_batch",
        )

    # Substack dispatch: always Friday 3pm ET
    scheduler.add_job(
        run_workflow,
        CronTrigger(day_of_week="fri", hour=15, timezone="America/New_York"),
        args=[agent, "substack_dispatch", SUBSTACK_DISPATCH_PROMPT],
        id="substack_dispatch",
    )

    # Business review: always Sunday 6pm ET
    scheduler.add_job(
        run_workflow,
        CronTrigger(day_of_week="sun", hour=18, timezone="America/New_York"),
        args=[agent, "business_review", BUSINESS_REVIEW_PROMPT],
        id="business_review",
    )
