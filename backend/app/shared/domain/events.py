"""
Standardized Domain Events Catalogue (ARC-04 §10, EVT-001 to EVT-018).
Pure Python dataclasses capturing completed business facts.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Base domain event carrying metadata, correlation context, and timestamp."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None
    causation_id: str | None = None
    schema_version: int = 1


# EVT-001: MOD-01 Identity
@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    user_id: UUID = field(default_factory=uuid4)
    email: str = ""


# EVT-002: MOD-02 Organization
@dataclass(frozen=True)
class OrganizationCreated(DomainEvent):
    organization_id: UUID = field(default_factory=uuid4)
    owner_id: UUID = field(default_factory=uuid4)
    name: str = ""


# EVT-003: MOD-02 Organization
@dataclass(frozen=True)
class MemberInvited(DomainEvent):
    organization_id: UUID = field(default_factory=uuid4)
    invitee_email: str = ""
    role: str = "member"


# EVT-004: MOD-03 Restaurant
@dataclass(frozen=True)
class RestaurantCreated(DomainEvent):
    restaurant_id: UUID = field(default_factory=uuid4)
    organization_id: UUID = field(default_factory=uuid4)
    slug: str = ""


# EVT-005: MOD-03 Restaurant
@dataclass(frozen=True)
class RestaurantDeactivated(DomainEvent):
    restaurant_id: UUID = field(default_factory=uuid4)
    reason: str = ""


# EVT-006: MOD-04 Menu
@dataclass(frozen=True)
class MenuCreated(DomainEvent):
    menu_id: UUID = field(default_factory=uuid4)
    restaurant_id: UUID = field(default_factory=uuid4)
    name: str = ""


# EVT-007: MOD-05 Category
@dataclass(frozen=True)
class CategoryCreated(DomainEvent):
    category_id: UUID = field(default_factory=uuid4)
    menu_id: UUID = field(default_factory=uuid4)
    name: str = ""
    display_order: int = 0


# EVT-008: MOD-06 Food Item
@dataclass(frozen=True)
class FoodItemCreated(DomainEvent):
    item_id: UUID = field(default_factory=uuid4)
    category_id: UUID = field(default_factory=uuid4)
    name: str = ""


# EVT-009: MOD-07 Pricing
@dataclass(frozen=True)
class ItemPriceChanged(DomainEvent):
    item_id: UUID = field(default_factory=uuid4)
    new_price: Decimal = Decimal("0.00")
    currency: str = "INR"


# EVT-010: MOD-08 Theme
@dataclass(frozen=True)
class ThemeUpdated(DomainEvent):
    restaurant_id: UUID = field(default_factory=uuid4)
    preset_id: str = "minimal-light"


# EVT-011: MOD-09 Layout
@dataclass(frozen=True)
class LayoutConfigurationChanged(DomainEvent):
    restaurant_id: UUID = field(default_factory=uuid4)
    layout_family: str = "list"


# EVT-012: MOD-10 Component Registry
@dataclass(frozen=True)
class ComponentRegistered(DomainEvent):
    component_id: str = ""
    version: int = 1


# EVT-013: MOD-12 Editor
@dataclass(frozen=True)
class DraftSaved(DomainEvent):
    restaurant_id: UUID = field(default_factory=uuid4)
    draft_id: UUID = field(default_factory=uuid4)


# EVT-014: MOD-13 Publishing
@dataclass(frozen=True)
class MenuPublished(DomainEvent):
    menu_id: UUID = field(default_factory=uuid4)
    publication_id: UUID = field(default_factory=uuid4)
    version_id: UUID = field(default_factory=uuid4)
    version_number: int = 1
    snapshot_hash: str = ""


# EVT-015: MOD-13 Publishing
@dataclass(frozen=True)
class PublicationRolledBack(DomainEvent):
    menu_id: UUID = field(default_factory=uuid4)
    target_version_id: UUID = field(default_factory=uuid4)
    version_number: int = 1


# EVT-016: MOD-14 Media
@dataclass(frozen=True)
class MediaUploaded(DomainEvent):
    asset_id: UUID = field(default_factory=uuid4)
    restaurant_id: UUID = field(default_factory=uuid4)
    content_type: str = "image/webp"


# EVT-017: MOD-15 Licensing
@dataclass(frozen=True)
class EntitlementUpdated(DomainEvent):
    organization_id: UUID = field(default_factory=uuid4)
    plan_code: str = "starter"


# EVT-018: MOD-16 Analytics
@dataclass(frozen=True)
class UsageEventRecorded(DomainEvent):
    event_type: str = "page_view"
    restaurant_id: UUID = field(default_factory=uuid4)
    metadata: dict[str, Any] = field(default_factory=dict)
