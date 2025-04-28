from logging.config import fileConfig
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from alembic import context
import logging
import traceback


# Load Alembic Config
config = context.config

# Set up logging
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.runtime.migration")

# Import models and metadata
from app.models.base import SQLModel  # Import all models explicitly
from app.core.config import settings

target_metadata = SQLModel.metadata

def get_url():
    return str(settings.SQLALCHEMY_DATABASE_URI)


def do_run_migrations(connection):
    try:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
    except Exception as e:
        logger.error(traceback.format_exc())
        raise

async def run_async_migrations():
    db_url = get_url()
    connectable = create_async_engine(db_url, poolclass=NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())

run_migrations_online()

