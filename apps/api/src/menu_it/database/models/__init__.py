"""Database models registry (FCD-04 §7.3)."""

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.organization import (
    Organization,
    OrganizationStatus,
    Tenant,
    TenantStatus,
)
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationMembership,
    OrganizationRole,
)
from menu_it.database.models.restaurant import (
    Restaurant,
    RestaurantStatus,
)
from menu_it.database.models.restaurant_membership import (
    RestaurantMembership,
    RestaurantRole,
)

__all__ = [
    "MembershipStatus",
    "Organization",
    "OrganizationAuditEvent",
    "OrganizationMembership",
    "OrganizationRole",
    "OrganizationStatus",
    "Restaurant",
    "RestaurantMembership",
    "RestaurantRole",
    "RestaurantStatus",
    "Tenant",
    "TenantStatus",
]
