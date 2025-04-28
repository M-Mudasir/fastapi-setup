import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlmodel import select
from tenacity import (
    AsyncRetrying,
    after_log,
    before_log,
    stop_after_attempt,
    wait_fixed,
)

from app.core.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


async def init(db_engine: AsyncEngine) -> None:
    try:
        async with AsyncSession(db_engine) as session:
            await session.execute(select(1))
    except Exception as e:
        logger.error(e)
        raise e


async def main() -> None:
    logger.info("Initializing service")
    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(max_tries),
        wait=wait_fixed(wait_seconds),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.WARN),
    ):
        with attempt:
            await init(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
