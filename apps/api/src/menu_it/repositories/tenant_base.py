"""Tenant-scoped base repository for organization-owned models (FCD-04 §11.2)."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.base import Base
from menu_it.tenancy.context import TenantContext

ModelType = TypeVar("ModelType", bound=Base)


class TenantScopedRepository(Generic[ModelType]):
    """Base repository that automatically enforces organization_id scoping on all queries.

    Every operation is restricted to self.context.organization_id.
    Mutations verify tenant ownership before applying changes.
    """

    def __init__(
        self,
        session: AsyncSession,
        context: TenantContext,
        model: type[ModelType],
    ):
        self.session = session
        self.context = context
        self.model = model

    async def get_by_id(
        self,
        record_id: UUID,
    ) -> ModelType | None:
        """Retrieve an entity by primary key strictly scoped to active organization."""
        statement = select(self.model).where(
            self.model.id == record_id,
            self.model.organization_id == self.context.organization_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Retrieve paginated entities scoped to active organization."""
        statement = (
            select(self.model)
            .where(self.model.organization_id == self.context.organization_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(
        self,
        instance: ModelType,
    ) -> ModelType:
        """Ensure organization_id matches active context and flush."""
        instance.organization_id = self.context.organization_id
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(
        self,
        instance: ModelType,
    ) -> ModelType:
        """Verify tenant ownership and flush updated state."""
        if instance.organization_id != self.context.organization_id:
            raise ValueError("Cannot update entity belonging to another organization")
        await self.session.flush()
        return instance

    async def delete(
        self,
        instance: ModelType,
    ) -> None:
        """Verify tenant ownership and flush delete."""
        if instance.organization_id != self.context.organization_id:
            raise ValueError("Cannot delete entity belonging to another organization")
        await self.session.delete(instance)
        await self.session.flush()
