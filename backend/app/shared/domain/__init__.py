"""
Shared pure domain package (entities, value objects, exceptions, events).
Zero external framework dependencies.
"""
from app.shared.domain.entities import MenuEntity
from app.shared.domain.exceptions import (
    BusinessRuleViolationException,
    DomainException,
    EntityNotFoundException,
)
from app.shared.domain.value_objects import (
    DisplayOrder,
    EmailAddress,
    MenuSlug,
    Money,
    RestaurantSlug,
)
from app.shared.domain.events import (
    DomainEvent,
    UserRegistered,
    OrganizationCreated,
    MemberInvited,
    RestaurantCreated,
    RestaurantDeactivated,
    MenuCreated,
    CategoryCreated,
    FoodItemCreated,
    ItemPriceChanged,
    ThemeUpdated,
    LayoutConfigurationChanged,
    ComponentRegistered,
    DraftSaved,
    MenuPublished,
    PublicationRolledBack,
    MediaUploaded,
    EntitlementUpdated,
    UsageEventRecorded,
)

from app.shared.domain.permissions import Permission
from app.shared.domain.tenant_exceptions import (
    TenantSecurityException,
    TenantAccessDeniedException,
    CrossTenantAccessException,
    InvalidTenantContextException,
    TenantSuspendedException,
    TenantResourceNotFoundException,
    TenantRelationalIntegrityException,
)

__all__ = [
    "MenuEntity",
    "DomainException",
    "EntityNotFoundException",
    "BusinessRuleViolationException",
    "Money",
    "EmailAddress",
    "RestaurantSlug",
    "MenuSlug",
    "DisplayOrder",
    "Permission",
    "TenantSecurityException",
    "TenantAccessDeniedException",
    "CrossTenantAccessException",
    "InvalidTenantContextException",
    "TenantSuspendedException",
    "TenantResourceNotFoundException",
    "TenantRelationalIntegrityException",
    "DomainEvent",
    "UserRegistered",
    "OrganizationCreated",
    "MemberInvited",
    "RestaurantCreated",
    "RestaurantDeactivated",
    "MenuCreated",
    "CategoryCreated",
    "FoodItemCreated",
    "ItemPriceChanged",
    "ThemeUpdated",
    "LayoutConfigurationChanged",
    "ComponentRegistered",
    "DraftSaved",
    "MenuPublished",
    "PublicationRolledBack",
    "MediaUploaded",
    "EntitlementUpdated",
    "UsageEventRecorded",
]
