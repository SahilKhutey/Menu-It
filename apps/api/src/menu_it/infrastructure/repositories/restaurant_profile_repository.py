"""SQLAlchemy adapter for RestaurantProfileRepository port (FCD-06 §14.3)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.restaurant_profile import RestaurantProfileRecord
from menu_it.domain.base.errors import ConcurrencyConflictError
from menu_it.domain.ports.repositories import RestaurantProfileRepository
from menu_it.domain.restaurant.profile import RestaurantProfile
from menu_it.infrastructure.mappers.restaurant_profile_mapper import (
    RestaurantProfileMapper,
)


class SQLAlchemyRestaurantProfileRepository(RestaurantProfileRepository):
    """SQLAlchemy implementation of RestaurantProfileRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, profile_id: UUID) -> RestaurantProfile | None:
        """Retrieve a restaurant profile by aggregate ID."""
        stmt = select(RestaurantProfileRecord).where(RestaurantProfileRecord.id == profile_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if record is None:
            return None
        return RestaurantProfileMapper.to_domain(record)

    async def get_by_restaurant_id(
        self,
        restaurant_id: UUID,
        organization_id: UUID,
    ) -> RestaurantProfile | None:
        """Retrieve a restaurant profile scoped by restaurant and organization ID."""
        stmt = select(RestaurantProfileRecord).where(
            RestaurantProfileRecord.restaurant_id == restaurant_id,
            RestaurantProfileRecord.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if record is None:
            return None
        return RestaurantProfileMapper.to_domain(record)

    async def save(self, profile: RestaurantProfile) -> None:
        """Persist or update restaurant profile aggregate root with optimistic concurrency check."""
        stmt = select(RestaurantProfileRecord).where(RestaurantProfileRecord.id == profile.id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            # Concurrency check: database version must be strictly less than aggregate version
            if existing.version >= profile.version:
                raise ConcurrencyConflictError(
                    f"Concurrency conflict: profile {profile.id} has version {existing.version}, "
                    f"cannot save stale version {profile.version}."
                )
            RestaurantProfileMapper.to_record(profile, existing)
        else:
            new_record = RestaurantProfileMapper.to_record(profile)
            self.session.add(new_record)

        await self.session.flush()
