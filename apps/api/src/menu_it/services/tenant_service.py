"""Application service managing tenant operations with atomic transactions (FCD-03 §13.2)."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.restaurant import Restaurant
from menu_it.database.models.tenant import Tenant
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.repositories.restaurants import RestaurantRepository
from menu_it.repositories.tenants import TenantRepository


class TenantService:
    """Service coordinating multi-repository operations within atomic transaction boundaries."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.tenants = TenantRepository(session)
        self.restaurants = RestaurantRepository(session)

    async def create_tenant_with_restaurant(
        self,
        *,
        tenant_name: str,
        tenant_slug: str,
        restaurant_name: str,
        restaurant_slug: str,
        timezone: str = "UTC",
    ) -> tuple[Tenant, Restaurant]:
        """Atomically create a tenant and its primary restaurant.

        Guarantees that either both are created and committed or neither is created.
        Translates unique constraint violations into ResourceConflictError.
        """
        try:
            async with self.session.begin():
                # Preliminary check for user-friendly error messaging
                if await self.tenants.slug_exists(tenant_slug):
                    raise ResourceConflictError(
                        f"Tenant slug '{tenant_slug}' is already registered."
                    )

                tenant = Tenant(
                    name=tenant_name,
                    slug=tenant_slug,
                )
                await self.tenants.create(tenant)

                restaurant = Restaurant(
                    tenant_id=tenant.id,
                    name=restaurant_name,
                    slug=restaurant_slug,
                    timezone=timezone,
                )
                await self.restaurants.create(restaurant)

                return tenant, restaurant
        except IntegrityError as exc:
            # Transaction has rolled back automatically
            raise ResourceConflictError(
                "A database uniqueness or integrity constraint was violated during tenant creation."
            ) from exc
