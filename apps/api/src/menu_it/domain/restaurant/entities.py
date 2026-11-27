"""Restaurant domain entities and invariants (FCD-14 WP-01)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.restaurant.lifecycle import RestaurantLifecycleState
from menu_it.domain.value_objects.slug import Slug
from menu_it.domain.value_objects.timezone import TimeZone


@dataclass(frozen=True, slots=True)
class RestaurantEntity:
    """Pure domain entity representing a restaurant business unit owned by an organization."""

    id: UUID
    organization_id: UUID
    name: str
    slug: str
    timezone: str
    status: str
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    cuisine_type: str | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None

    def __post_init__(self) -> None:
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationDomainError("Restaurant name must be at least 2 characters.")
        Slug(self.slug)
        TimeZone(self.timezone)
        RestaurantLifecycleState.from_value(self.status)
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValidationDomainError("Restaurant timestamps must be timezone-aware UTC.")


@dataclass(frozen=True, slots=True)
class RestaurantSettingsEntity:
    """Pure domain entity representing restaurant-level regional/operational settings."""

    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    settings_payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
