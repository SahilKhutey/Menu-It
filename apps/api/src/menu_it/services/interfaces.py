"""Cross-module service interfaces and protocols (FCD-07 WP-12)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.services.results import ApplicationResult


@dataclass(frozen=True)
class RestaurantLookupDTO:
    """Read-only data transfer object for cross-module restaurant queries."""

    id: UUID
    organization_id: UUID
    name: str
    slug: str
    timezone: str
    status: str
    created_at: datetime
    updated_at: datetime


class RestaurantQueryService(Protocol):
    """Protocol defining cross-module restaurant query capabilities."""

    async def get_restaurant(
        self,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> ApplicationResult[RestaurantLookupDTO]:
        """Query restaurant details within organization boundary."""
        ...

    async def is_restaurant_active(
        self,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> ApplicationResult[bool]:
        """Check whether a restaurant is active and accessible."""
        ...


class DefaultRestaurantQueryService:
    """Concrete implementation of RestaurantQueryService."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_restaurant(
        self,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> ApplicationResult[RestaurantLookupDTO]:
        """Query restaurant ensuring organization boundary."""
        stmt = select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.organization_id == organization_id,
        )
        result = await self._session.execute(stmt)
        restaurant = result.scalar_one_or_none()

        if restaurant is None:
            return ApplicationResult.fail(
                error=(
                    f"Restaurant '{restaurant_id}' not found in organization '{organization_id}'."
                ),
                error_code="RESTAURANT_NOT_FOUND",
            )

        dto = RestaurantLookupDTO(
            id=restaurant.id,
            organization_id=restaurant.organization_id,
            name=restaurant.name,
            slug=restaurant.slug,
            timezone=restaurant.timezone,
            status=restaurant.status.value,
            created_at=restaurant.created_at,
            updated_at=restaurant.updated_at,
        )
        return ApplicationResult.ok(dto)

    async def is_restaurant_active(
        self,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> ApplicationResult[bool]:
        """Verify restaurant exists and status is ACTIVE."""
        stmt = select(Restaurant.status).where(
            Restaurant.id == restaurant_id,
            Restaurant.organization_id == organization_id,
        )
        result = await self._session.execute(stmt)
        status_val = result.scalar_one_or_none()

        if status_val is None:
            return ApplicationResult.fail(
                error=f"Restaurant '{restaurant_id}' not found.",
                error_code="RESTAURANT_NOT_FOUND",
            )

        is_active = status_val == RestaurantStatus.ACTIVE
        return ApplicationResult.ok(is_active)
