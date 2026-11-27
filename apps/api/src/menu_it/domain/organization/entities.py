"""Organization domain entities and invariants (FCD-14 WP-01)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.slug import Slug
from menu_it.domain.value_objects.timezone import TimeZone


def validate_country_code(code: str) -> str:
    """Validate ISO 3166-1 alpha-2 two-letter country code."""
    if not isinstance(code, str) or len(code.strip()) != 2 or not code.strip().isalpha():
        raise ValidationDomainError(f"Invalid ISO-3166 alpha-2 country code: '{code}'.")
    return code.strip().upper()


@dataclass(frozen=True, slots=True)
class OrganizationEntity:
    """Pure domain entity representing a tenant organization."""

    id: UUID
    name: str
    slug: str
    status: str
    country_code: str
    currency_code: str
    timezone: str
    created_at: datetime
    updated_at: datetime
    legal_name: str | None = None
    organization_type: str = "company"
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None

    def __post_init__(self) -> None:
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationDomainError("Organization name must be at least 2 characters.")
        Slug(self.slug)
        Currency(self.currency_code)
        TimeZone(self.timezone)
        validate_country_code(self.country_code)
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValidationDomainError("Organization timestamps must be timezone-aware UTC.")


@dataclass(frozen=True, slots=True)
class OrganizationSettingsEntity:
    """Pure domain entity representing organization-level configuration."""

    id: UUID
    organization_id: UUID
    settings_payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
