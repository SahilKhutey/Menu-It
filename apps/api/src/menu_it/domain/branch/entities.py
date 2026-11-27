"""Branch domain entity and invariants (FCD-14 WP-01)."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.branch.lifecycle import BranchLifecycleState
from menu_it.domain.organization.entities import validate_country_code
from menu_it.domain.value_objects.slug import Slug
from menu_it.domain.value_objects.timezone import TimeZone


@dataclass(frozen=True, slots=True)
class BranchReference:
    """Lightweight domain reference to a branch scoped by restaurant and organization."""

    branch_id: UUID
    restaurant_id: UUID
    organization_id: UUID
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class BranchEntity:
    """Pure domain entity representing a physical or operational restaurant branch."""

    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    name: str
    slug: str
    timezone: str
    country_code: str
    status: str
    created_at: datetime
    updated_at: datetime
    branch_code: str | None = None
    email: str | None = None
    phone: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state_region: str | None = None
    postal_code: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None

    def __post_init__(self) -> None:
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationDomainError("Branch name must be at least 2 characters.")
        Slug(self.slug)
        TimeZone(self.timezone)
        validate_country_code(self.country_code)
        BranchLifecycleState.from_value(self.status)
        if self.latitude is not None and (
            self.latitude < Decimal("-90") or self.latitude > Decimal("90")
        ):
            raise ValidationDomainError("Latitude must be between -90 and 90.")
        if self.longitude is not None and (
            self.longitude < Decimal("-180") or self.longitude > Decimal("180")
        ):
            raise ValidationDomainError("Longitude must be between -180 and 180.")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValidationDomainError("Branch timestamps must be timezone-aware UTC.")
