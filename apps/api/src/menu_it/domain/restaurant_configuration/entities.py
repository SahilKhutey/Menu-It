"""Domain entities for branding, branch configuration, and public profile publication."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from menu_it.domain.base.errors import InvalidStateTransitionError
from menu_it.domain.restaurant_configuration.schedule import ScheduleExceptionEntry
from menu_it.domain.restaurant_configuration.value_objects import (
    HexColor,
    OpeningInterval,
    OperationalSettings,
    PublicationStatus,
    ServiceModeConfig,
)

ALLOWED_PUBLICATION_TRANSITIONS: dict[PublicationStatus, set[PublicationStatus]] = {
    PublicationStatus.DRAFT: {PublicationStatus.READY, PublicationStatus.PUBLISHED},
    PublicationStatus.READY: {PublicationStatus.PUBLISHED, PublicationStatus.DRAFT},
    PublicationStatus.PUBLISHED: {
        PublicationStatus.PUBLISHED,
        PublicationStatus.UNPUBLISHED,
        PublicationStatus.ARCHIVED,
    },
    PublicationStatus.UNPUBLISHED: {
        PublicationStatus.PUBLISHED,
        PublicationStatus.ARCHIVED,
    },
    PublicationStatus.ARCHIVED: set(),
}


@dataclass(frozen=True)
class RestaurantBrandingEntity:
    """Visual identity and validated theme settings for a restaurant."""

    organization_id: UUID
    restaurant_id: UUID
    logo_asset_id: UUID | None = None
    alternate_logo_asset_id: UUID | None = None
    cover_asset_id: UUID | None = None
    favicon_asset_id: UUID | None = None
    primary_color: HexColor | None = None
    secondary_color: HexColor | None = None
    accent_color: HexColor | None = None
    background_color: HexColor | None = None
    text_color: HexColor | None = None
    font_family: str | None = None
    border_radius: str | None = None
    theme_preset: str | None = None
    theme_settings: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BranchConfigurationEntity:
    """Explicit branch-level overrides over restaurant configuration."""

    organization_id: UUID
    restaurant_id: UUID
    branch_id: UUID
    display_name_override: str | None = None
    public_phone_override: str | None = None
    schedule_override_enabled: bool = False
    service_override_enabled: bool = False
    operational_settings_override: OperationalSettings | None = None
    service_overrides: dict[str, ServiceModeConfig | None] = field(default_factory=dict)
    weekly_hours_override: dict[int, tuple[OpeningInterval, ...]] = field(default_factory=dict)
    schedule_exceptions_override: tuple[ScheduleExceptionEntry, ...] = ()


@dataclass(frozen=True)
class PublicProfilePublicationEntity:
    """Publication pointer and validation rules for public restaurant profiles."""

    organization_id: UUID
    restaurant_id: UUID
    public_slug: str
    status: PublicationStatus
    published_revision: int | None = None
    published_at: datetime | None = None

    def validate_transition(self, target: PublicationStatus) -> None:
        """Ensure publication status transition is permitted."""
        allowed = ALLOWED_PUBLICATION_TRANSITIONS.get(self.status, set())
        if target not in allowed:
            raise InvalidStateTransitionError(
                f"Cannot transition publication from '{self.status}' to '{target}'."
            )


@dataclass(frozen=True)
class EffectiveRestaurantConfiguration:
    """Resolved deterministic configuration snapshot for a restaurant or branch."""

    organization_id: UUID
    restaurant_id: UUID
    branch_id: UUID | None
    display_name: str
    timezone: str
    currency_code: str
    public_phone: str | None
    enabled_services: tuple[str, ...]
    services: dict[str, ServiceModeConfig]
    weekly_hours: dict[int, tuple[OpeningInterval, ...]]
    schedule_exceptions: tuple[ScheduleExceptionEntry, ...]
    branding: RestaurantBrandingEntity | None
    operational_settings: OperationalSettings
    revision: int
