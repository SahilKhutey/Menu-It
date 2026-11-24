"""SQLAlchemy async engine and connection pool manager (FCD-03 §7)."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)

from menu_it.core.config import settings


def create_database_engine(
    database_url: str | None = None,
) -> AsyncEngine:
    """Create and configure an asynchronous SQLAlchemy engine."""
    url = database_url or settings.database_url

    # SQLite dialect (used in lightweight unit tests) does not support pool sizing parameters
    if "sqlite" in str(url):
        return create_async_engine(
            url,
            echo=settings.database_echo,
            pool_pre_ping=True,
        )

    return create_async_engine(
        url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        pool_recycle=settings.database_pool_recycle,
        pool_pre_ping=True,
    )


# Application-level engine singleton
engine: AsyncEngine = create_database_engine()
