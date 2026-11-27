"""Organization invitation domain entity (FCD-14 WP-01)."""

import enum
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.membership.entities import VALID_ORG_ROLES


class InvitationStatus(enum.StrEnum):
    """Lifecycle states of an organization invitation."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class OrganizationInvitationEntity:
    """Pure domain entity for an organization membership invitation."""

    id: UUID
    organization_id: UUID
    email: str
    role: str
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime
    invited_by: UUID | None = None
    accepted_by: UUID | None = None
    accepted_at: datetime | None = None

    def __post_init__(self) -> None:
        if "@" not in self.email or not self.email.strip():
            raise ValidationDomainError("Invitation email must be a valid email address.")
        if self.role not in VALID_ORG_ROLES or self.role == "owner":
            raise ValidationDomainError(
                f"Invitation role '{self.role}' is invalid or cannot be invited directly as owner."
            )
        if self.expires_at.tzinfo is None or self.created_at.tzinfo is None:
            raise ValidationDomainError("Invitation timestamps must be timezone-aware UTC.")
