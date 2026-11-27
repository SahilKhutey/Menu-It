"""Repository ports defining domain persistence contracts (FCD-06 §11.1)."""

from typing import Protocol
from uuid import UUID

from menu_it.domain.restaurant.profile import RestaurantProfile


class RestaurantProfileRepository(Protocol):
    """Port for persisting and retrieving RestaurantProfile aggregate roots."""

    async def get_by_id(self, profile_id: UUID) -> RestaurantProfile | None:
        """Retrieve a restaurant profile by its aggregate ID."""
        ...

    async def get_by_restaurant_id(
        self,
        restaurant_id: UUID,
        organization_id: UUID,
    ) -> RestaurantProfile | None:
        """Retrieve a restaurant profile scoped by restaurant and organization ID."""
        ...

    async def save(self, profile: RestaurantProfile) -> None:
        """Save a new or modified restaurant profile aggregate root."""
        ...
