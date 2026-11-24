"""Database session management and dependency injection (FCD-03 §11.1)."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from menu_it.database.engine import engine

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Provide a request-scoped database session.

    Rules:
    - One request gets one session.
    - The same session can be passed to multiple repositories.
    - The dependency closes the session after the request finishes.
    - Does NOT automatically commit business operations (services own transactions).
    """
    async with AsyncSessionFactory() as session:
        yield session
