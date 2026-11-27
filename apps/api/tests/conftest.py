"""Shared test fixtures for the Menu-It backend API (FCD-03 §15.4)."""

import os
from collections.abc import AsyncIterator
from urllib.parse import urlparse

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from menu_it.application import create_application
from menu_it.database import models  # noqa: F401
from menu_it.database.base import Base


@pytest.fixture
def app():
    """Create a fresh FastAPI application instance for testing."""
    return create_application()


@pytest.fixture
def client(app):
    """Provide a TestClient within the application lifespan context."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authed_client(app, db_session: AsyncSession):
    """Provide a TestClient with get_db_session wired to the active test database session."""
    from menu_it.database.session import get_db_session

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = _override_get_db
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_engine() -> AsyncIterator[AsyncEngine]:
    """Provide an isolated asynchronous database engine for integration tests.

    Follows FCD-03 §15.4 & §19.1 safeguards:
    - If DATABASE_TEST_URL is configured, strictly verifies the target is a test database
      (refusing destructive drops against production/development environments).
    - If DATABASE_TEST_URL is not set, provisions an isolated in-memory SQLite engine
      with StaticPool to guarantee fast, zero-dependency local execution.
    """
    database_url = os.environ.get("DATABASE_TEST_URL")

    if database_url:
        parsed = urlparse(database_url)
        db_name = parsed.path.lstrip("/")
        if not db_name.endswith("_test"):
            raise RuntimeError(
                f"Refusing to run destructive test setup against non-test database: {db_name}"
            )
        engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
        )
    else:
        # High-speed in-memory database for local test runs
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    # Enable foreign key enforcement on SQLite
    if "sqlite" in str(engine.url):
        from sqlalchemy import event

        @event.listens_for(engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Provide a clean request-isolated async session for test execution."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()
