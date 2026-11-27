"""Restaurant domain reference carrying explicit organization ownership (FCD-06 §8.2)."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RestaurantReference:
    """Lightweight domain reference to a restaurant and its owning organization."""

    restaurant_id: UUID
    organization_id: UUID
    display_name: str | None = None
