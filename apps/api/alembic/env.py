"""Alembic environment configuration for async SQLAlchemy (FCD-03 §10.3)."""

import asyncio
import concurrent.futures
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Ensure apps/api/src is in sys.path
api_src = Path(__file__).resolve().parents[1] / "src"
if str(api_src) not in sys.path:
    sys.path.insert(0, str(api_src))

from menu_it.core.config import settings
from menu_it.database import models  # noqa: F401
from menu_it.database.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Return database URL from Alembic config, environment or settings."""
    cfg_url = config.get_main_option("sqlalchemy.url")
    if cfg_url:
        return cfg_url
    return os.environ.get("DATABASE_URL") or settings.database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode without an active database connection."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations synchronously inside an engine connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create async engine and execute migration script runner."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode, supporting both async and sync drivers."""
    url = get_url()

    if "+asyncpg" in url or "+aiosqlite" in url:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(asyncio.run, run_async_migrations()).result()
        else:
            asyncio.run(run_async_migrations())
    else:
        configuration = config.get_section(config.config_ini_section) or {}
        configuration["sqlalchemy.url"] = url

        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            do_run_migrations(connection)

        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
