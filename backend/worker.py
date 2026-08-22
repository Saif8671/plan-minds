import asyncio
import logging

from app.core.config import get_settings
from app.core.logger import setup_logging
from app.core.scheduler import start_scheduler, stop_scheduler

settings = get_settings()


async def main():
    setup_logging(settings.log_level)
    logger = logging.getLogger("worker")
    logger.info("Starting PlanMinds standalone scheduler worker...")

    start_scheduler()

    try:
        # Keep the main thread alive while apscheduler runs in the background
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Worker shutting down...")
    finally:
        stop_scheduler()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
