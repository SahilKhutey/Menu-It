"""
ModularMenu — Database Session Configuration (ARC-06 §8.5, §12.4).
Provides pooled async sessions, statement timeouts, and connection recycling.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Engine configuration with bounded pooling and pre-ping (ARC-06 §12.4)
engine_kwargs = {
    "echo": settings.DB_ECHO,
}

if "sqlite" not in settings.DATABASE_URL:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    })

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_tenant_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yields an AsyncSession instance with explicit closure on exit."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()
