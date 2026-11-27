"""Organization invitation lifecycle transitions and acceptance rules (FCD-14 WP-01)."""

from datetime import datetime

from menu_it.domain.base.errors import InvalidStateTransitionError, ValidationDomainError
from menu_it.domain.invitation.entities import InvitationStatus, OrganizationInvitationEntity

ALLOWED_INVITATION_TRANSITIONS: dict[InvitationStatus, set[InvitationStatus]] = {
    InvitationStatus.PENDING: {
        InvitationStatus.ACCEPTED,
        InvitationStatus.REVOKED,
        InvitationStatus.EXPIRED,
    },
    InvitationStatus.ACCEPTED: set(),
    InvitationStatus.REVOKED: set(),
    InvitationStatus.EXPIRED: set(),
}


def validate_invitation_transition(
    current: InvitationStatus,
    target: InvitationStatus,
) -> None:
    """Validate that an invitation state transition is allowed."""
    if current == target:
        return
    if target not in ALLOWED_INVITATION_TRANSITIONS.get(current, set()):
        raise InvalidStateTransitionError(
            f"Cannot transition invitation from '{current.value}' to '{target.value}'."
        )


def ensure_invitation_acceptable(
    invitation: OrganizationInvitationEntity,
    *,
    now: datetime,
    actor_email: str,
) -> None:
    """Validate that an invitation is pending, unexpired, and matches the accepting user."""
    if invitation.status == InvitationStatus.REVOKED:
        raise InvalidStateTransitionError("Invitation has been revoked.")
    if invitation.status == InvitationStatus.ACCEPTED:
        raise InvalidStateTransitionError("Invitation has already been accepted.")
    if invitation.status == InvitationStatus.EXPIRED or invitation.expires_at <= now:
        raise InvalidStateTransitionError("Invitation has expired.")
    if invitation.email.strip().lower() != actor_email.strip().lower():
        raise ValidationDomainError("Invitation email does not match the authenticated user.")
