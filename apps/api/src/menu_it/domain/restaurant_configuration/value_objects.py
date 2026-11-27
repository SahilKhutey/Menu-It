"""Domain value objects for FCD-15 restaurant configuration."""

import enum
import re
from dataclasses import dataclass
from datetime import time

from menu_it.domain.base.errors import ValidationDomainError

HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


class ServiceType(enum.StrEnum):
    """Supported restaurant fulfillment service modes."""

    DINE_IN = "DINE_IN"
    TAKEAWAY = "TAKEAWAY"
    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"
    CURBSIDE_PICKUP = "CURBSIDE_PICKUP"


class ExceptionType(enum.StrEnum):
    """Types of date-specific schedule exceptions."""

    CLOSED = "CLOSED"
    SPECIAL_HOURS = "SPECIAL_HOURS"
    REDUCED_HOURS = "REDUCED_HOURS"
    EXTENDED_HOURS = "EXTENDED_HOURS"


class PublicationStatus(enum.StrEnum):
    """Lifecycle states of a public restaurant profile publication."""

    DRAFT = "draft"
    READY = "ready"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"
    ARCHIVED = "archived"


@dataclass(frozen=True, slots=True)
class HexColor:
    """Validated six-digit hexadecimal color value."""

    value: str

    def __post_init__(self) -> None:
        if not HEX_COLOR_PATTERN.fullmatch(self.value):
            raise ValidationDomainError(
                f"Color '{self.value}' must be a six-digit hex value (e.g., #FF5733)."
            )

    def normalized(self) -> str:
        """Return uppercase normalized hex color string."""
        return self.value.upper()


@dataclass(frozen=True, slots=True)
class OpeningInterval:
    """Single opening hours interval, optionally spanning midnight."""

    opens_at: time
    closes_at: time
    closes_next_day: bool = False

    def __post_init__(self) -> None:
        if self.opens_at == self.closes_at and not self.closes_next_day:
            raise ValidationDomainError("Opening interval cannot have zero duration.")
        if not self.closes_next_day and self.closes_at < self.opens_at:
            raise ValidationDomainError(
                "Closing time earlier than opening time requires closes_next_day=True."
            )

    def to_minute_span(self) -> tuple[int, int]:
        """Convert interval to [start_minute, end_minute) from 00:00 of start day."""
        start = self.opens_at.hour * 60 + self.opens_at.minute
        end = self.closes_at.hour * 60 + self.closes_at.minute
        if self.closes_next_day:
            end += 24 * 60
        return start, end

    def overlaps_with(self, other: "OpeningInterval") -> bool:
        """Return True if this interval overlaps with another interval on the same day."""
        s1, e1 = self.to_minute_span()
        s2, e2 = other.to_minute_span()
        return s1 < e2 and s2 < e1


@dataclass(frozen=True, slots=True)
class ServiceModeConfig:
    """Typed configuration for a restaurant or branch service mode."""

    service_type: ServiceType
    enabled: bool
    requires_customer_address: bool = False
    accepts_scheduled_orders: bool = False
    minimum_notice_minutes: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.service_type, ServiceType):
            object.__setattr__(self, "service_type", ServiceType(self.service_type))
        if self.minimum_notice_minutes < 0:
            raise ValidationDomainError("minimum_notice_minutes cannot be negative.")


@dataclass(frozen=True, slots=True)
class OperationalSettings:
    """Validated operational preferences for preparation and capacity."""

    preparation_buffer_minutes: int = 15
    minimum_notice_minutes: int = 0
    maximum_advance_days: int = 7
    max_concurrent_orders: int | None = None
    auto_accept_orders: bool = False
    holiday_behavior: str = "follow_exceptions"

    def __post_init__(self) -> None:
        if self.preparation_buffer_minutes < 0:
            raise ValidationDomainError("Preparation buffer cannot be negative.")
        if self.minimum_notice_minutes < 0:
            raise ValidationDomainError("Minimum notice cannot be negative.")
        if self.maximum_advance_days < 0:
            raise ValidationDomainError("Advance window cannot be negative.")
        if self.max_concurrent_orders is not None and self.max_concurrent_orders < 1:
            raise ValidationDomainError("max_concurrent_orders must be positive when set.")
