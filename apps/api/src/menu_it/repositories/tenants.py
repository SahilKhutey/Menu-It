"""Tenant repository for tenant data access (FCD-03 §12.3)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.tenant import Tenant
from menu_it.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """Repository handling Tenant queries and persistence."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Tenant)

    async def get_by_slug(
        self,
        slug: str,
    ) -> Tenant | None:
        """Look up a tenant by unique slug."""
        statement = select(Tenant).where(Tenant.slug == slug)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def slug_exists(
        self,
        slug: str,
    ) -> bool:
        """Check if a tenant slug is already registered."""
        statement = select(Tenant.id).where(Tenant.slug == slug)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() is not None
