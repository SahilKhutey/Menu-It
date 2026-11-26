"""Database models registry (FCD-04 §7.3)."""

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.background_job import BackgroundJobModel
from menu_it.database.models.credential import UserCredential
from menu_it.database.models.dead_letter_job import DeadLetterJobModel
from menu_it.database.models.event_outbox import EventOutboxModel
from menu_it.database.models.file import FileModel
from menu_it.database.models.idempotency import IdempotencyRecord
from menu_it.database.models.notification import (
    NotificationDeliveryModel,
    NotificationModel,
)
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
from menu_it.database.models.processed_event import ProcessedEventModel
from menu_it.database.models.recovery import PasswordResetToken
from menu_it.database.models.restaurant import (
    Restaurant,
    RestaurantStatus,
)
from menu_it.database.models.restaurant_membership import (
    RestaurantMembership,
    RestaurantRole,
)
from menu_it.database.models.restaurant_profile import RestaurantProfileRecord
from menu_it.database.models.scheduled_job import (
    ScheduledJobModel,
    ScheduledJobRunModel,
)
from menu_it.database.models.security_audit import SecurityAuditEventModel
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
    "BackgroundJobModel",
    "DeadLetterJobModel",
    "EmailVerificationToken",
    "EventOutboxModel",
    "FileModel",
    "IdempotencyRecord",
    "MembershipStatus",
    "NotificationDeliveryModel",
    "NotificationModel",
    "Organization",
    "OrganizationAuditEvent",
    "OrganizationMembership",
    "OrganizationRole",
    "OrganizationStatus",
    "PasswordResetToken",
    "PlatformMembership",
    "PlatformMembershipStatus",
    "PlatformRole",
    "ProcessedEventModel",
    "RefreshTokenRecord",
    "Restaurant",
    "RestaurantMembership",
    "RestaurantProfileRecord",
    "RestaurantRole",
    "RestaurantStatus",
    "ScheduledJobModel",
    "ScheduledJobRunModel",
    "SecurityAuditEventModel",
    "SessionStatus",
    "Tenant",
    "TenantStatus",
    "User",
    "UserCredential",
    "UserSession",
    "UserStatus",
    "normalize_email",
]
