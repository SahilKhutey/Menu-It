"""Database models registry (FCD-04 §7.3)."""

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.credential import UserCredential
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
from menu_it.database.models.platform import (
    PlatformMembership,
    PlatformMembershipStatus,
    PlatformRole,
)
from menu_it.database.models.recovery import PasswordResetToken
from menu_it.database.models.restaurant import (
    Restaurant,
    RestaurantStatus,
)
from menu_it.database.models.restaurant_membership import (
    RestaurantMembership,
    RestaurantRole,
)
from menu_it.database.models.session import (
    RefreshTokenRecord,
    SessionStatus,
    UserSession,
)
from menu_it.database.models.user import (
    User,
    UserStatus,
    normalize_email,
)
from menu_it.database.models.verification import EmailVerificationToken

__all__ = [
    "EmailVerificationToken",
    "MembershipStatus",
    "Organization",
    "OrganizationAuditEvent",
    "OrganizationMembership",
    "OrganizationRole",
    "OrganizationStatus",
    "PasswordResetToken",
    "PlatformMembership",
    "PlatformMembershipStatus",
    "PlatformRole",
    "RefreshTokenRecord",
    "Restaurant",
    "RestaurantMembership",
    "RestaurantRole",
    "RestaurantStatus",
    "SessionStatus",
    "Tenant",
    "TenantStatus",
    "User",
    "UserCredential",
    "UserSession",
    "UserStatus",
    "normalize_email",
]
