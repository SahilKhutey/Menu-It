"""Restaurant domain events (FCD-06 §10)."""

from dataclasses import dataclass
from uuid import UUID

from menu_it.domain.base.domain_event import DomainEvent


@dataclass(frozen=True, slots=True)
class RestaurantProfileUpdated(DomainEvent):
    """Emitted when restaurant business profile metadata is modified."""

    event_type: str = "restaurant.profile_updated"
    profile_id: UUID | None = None
    changed_fields: tuple[str, ...] = ()
    version: int = 1


@dataclass(frozen=True, slots=True)
class RestaurantStatusChanged(DomainEvent):
    """Emitted when a restaurant's operational lifecycle state transitions."""

    event_type: str = "restaurant.status_changed"
    previous_status: str = ""
    new_status: str = ""
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class RestaurantOperatingHoursUpdated(DomainEvent):
    """Emitted when a restaurant's weekly operating schedule is modified."""

    event_type: str = "restaurant.operating_hours_updated"
    profile_id: UUID | None = None
    version: int = 1
