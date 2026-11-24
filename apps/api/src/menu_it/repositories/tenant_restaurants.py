"""Tenant-scoped restaurant repository (FCD-04 §11.3)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.restaurant import Restaurant
from menu_it.repositories.tenant_base import TenantScopedRepository
from menu_it.tenancy.context import TenantContext


class TenantRestaurantRepository(TenantScopedRepository[Restaurant]):
    """Tenant-scoped data access for restaurants."""

    def __init__(self, session: AsyncSession, context: TenantContext):
        super().__init__(session, context, Restaurant)

    async def list_restaurants(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Restaurant]:
        """List restaurants owned by the current organization in creation order."""
        statement = (
            select(Restaurant)
            .where(Restaurant.organization_id == self.context.organization_id)
            .order_by(Restaurant.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_slug(
        self,
        slug: str,
    ) -> Restaurant | None:
        """Lookup restaurant by slug scoped to active organization."""
        statement = select(Restaurant).where(
            Restaurant.organization_id == self.context.organization_id,
            Restaurant.slug == slug,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
