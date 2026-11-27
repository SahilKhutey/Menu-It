"""Organization lifecycle state machine and transitions (FCD-04 §14)."""

from menu_it.database.models.organization import (
    Organization,
    OrganizationStatus,
)

ALLOWED_TRANSITIONS: dict[OrganizationStatus, set[OrganizationStatus]] = {
    OrganizationStatus.PROVISIONING: {
        OrganizationStatus.ACTIVE,
        OrganizationStatus.DEACTIVATED,
    },
    OrganizationStatus.ACTIVE: {
        OrganizationStatus.SUSPENDED,
        OrganizationStatus.OFFBOARDING,
    },
    OrganizationStatus.SUSPENDED: {
        OrganizationStatus.ACTIVE,
        OrganizationStatus.OFFBOARDING,
    },
    OrganizationStatus.OFFBOARDING: {
        OrganizationStatus.ACTIVE,
        OrganizationStatus.DEACTIVATED,
    },
    OrganizationStatus.DEACTIVATED: set(),
}


class InvalidOrganizationTransition(Exception):
    """Raised when an illegal organization lifecycle transition is attempted."""

    pass


def transition_organization(
    organization: Organization,
    target: OrganizationStatus,
) -> OrganizationStatus:
    """Validate and apply an organization lifecycle state transition.

    Enforces deterministic state transitions according to ARC-05 §8.
    """
    current = organization.status
    if current == target:
        return current

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidOrganizationTransition(
            f"Cannot transition organization from '{current}' to '{target}'."
        )

    organization.status = target
    return organization.status
