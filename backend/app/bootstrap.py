import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


async def initialize_database():
    """Initializes database engine and ensures metadata is registered."""
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully.")


async def close_database():
    """Closes all database connection pools cleanly."""
    logger.info("Disposing database connection pool...")
    await engine.dispose()
    logger.info("Database connection pool disposed.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager controlling startup and graceful shutdown."""
    configure_logging()
    logger.info("ModularMenu application bootstrapping...")
    await initialize_database()
    yield
    logger.info("ModularMenu application shutting down...")
    await close_database()
