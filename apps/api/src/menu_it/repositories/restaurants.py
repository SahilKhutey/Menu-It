"""Restaurant repository for restaurant data access (FCD-03 §12.4)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.restaurant import Restaurant
from menu_it.repositories.base import BaseRepository


class RestaurantRepository(BaseRepository[Restaurant]):
    """Repository handling Restaurant queries and persistence."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Restaurant)

    async def get_by_tenant_and_slug(
        self,
        tenant_id: UUID,
        slug: str,
    ) -> Restaurant | None:
        """Look up a restaurant by tenant UUID and restaurant slug."""
        statement = select(Restaurant).where(
            Restaurant.tenant_id == tenant_id,
            Restaurant.slug == slug,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Restaurant]:
        """List restaurants belonging to a specific tenant."""
        statement = (
            select(Restaurant).where(Restaurant.tenant_id == tenant_id).offset(offset).limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def slug_exists_for_tenant(
        self,
        tenant_id: UUID,
        slug: str,
    ) -> bool:
        """Check if a restaurant slug is already registered within a tenant."""
        statement = select(Restaurant.id).where(
            Restaurant.tenant_id == tenant_id,
            Restaurant.slug == slug,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() is not None
