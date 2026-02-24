"""Hobson agent entry point."""

import asyncio
import logging

import uvicorn
from langgraph.checkpoint.postgres import PostgresSaver

from hobson.agent import create_agent
from hobson.config import settings
from hobson.health import app
from hobson.scheduler import scheduler, setup_schedules

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting Hobson agent...")

    # Set up PostgreSQL checkpointer
    checkpointer = PostgresSaver.from_conn_string(settings.database_url)
    checkpointer.setup()
    logger.info("PostgreSQL checkpointer initialized")

    # Create agent
    agent = create_agent(checkpointer=checkpointer)
    logger.info("LangGraph agent compiled")

    # Set up scheduled workflows
    setup_schedules(agent)
    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))

    # Start health server
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    logger.info("Starting health server on :8080")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
