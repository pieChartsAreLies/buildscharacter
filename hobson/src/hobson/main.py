"""Hobson agent entry point."""

import asyncio
import logging

import uvicorn
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from hobson.agent import create_agent
from hobson.config import settings
from hobson.db import HobsonDB
from hobson.health import app
from hobson.scheduler import scheduler, setup_schedules
from hobson.tools.telegram import init_telegram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting Hobson agent...")

    # Set up async PostgreSQL checkpointer
    async with AsyncPostgresSaver.from_conn_string(settings.database_url) as checkpointer:
        await checkpointer.setup()
        logger.info("PostgreSQL checkpointer initialized (async)")

        # Create DB client and agent
        db = HobsonDB(settings.database_url)
        agent = create_agent(checkpointer=checkpointer)
        logger.info("LangGraph agent compiled")

        # Initialize Telegram bot with message handling
        telegram_app = init_telegram(agent, db)
        logger.info("Telegram bot initialized")

        # Set up scheduled workflows
        setup_schedules(agent)
        scheduler.start()
        logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))

        # Start health server
        health_config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
        health_server = uvicorn.Server(health_config)

        # Run Telegram polling + health server concurrently
        logger.info("Starting Telegram polling and health server on :8080")

        async with telegram_app:
            await telegram_app.initialize()
            await telegram_app.start()
            await telegram_app.updater.start_polling(drop_pending_updates=True)

            try:
                await health_server.serve()
            finally:
                await telegram_app.updater.stop()
                await telegram_app.stop()
                await telegram_app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
