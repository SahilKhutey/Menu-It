"""Generic base repository for model data access (FCD-03 §12.2)."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing standardized CRUD operations.

    Repositories do NOT commit or create independent sessions.
    All mutations call session.flush() to synchronize SQL state within
    the outer service transaction boundary.
    """

    def __init__(
        self,
        session: AsyncSession,
        model: type[ModelType],
    ):
        self.session = session
        self.model = model

    async def get_by_id(
        self,
        record_id: UUID,
    ) -> ModelType | None:
        """Retrieve a single entity by its primary key UUID."""
        return await self.session.get(self.model, record_id)

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Retrieve paginated entities."""
        statement = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(
        self,
        instance: ModelType,
    ) -> ModelType:
        """Add entity to session and flush changes without committing."""
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(
        self,
        instance: ModelType,
    ) -> ModelType:
        """Flush updated entity state to the database."""
        await self.session.flush()
        return instance

    async def delete(
        self,
        instance: ModelType,
    ) -> None:
        """Delete entity from session and flush."""
        await self.session.delete(instance)
        await self.session.flush()
