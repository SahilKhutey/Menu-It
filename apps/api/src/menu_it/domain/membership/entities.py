"""Membership and branch assignment domain entities (FCD-14 WP-01)."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from menu_it.domain.base.errors import ValidationDomainError

VALID_ORG_ROLES = frozenset({"owner", "admin", "manager", "staff", "viewer"})
VALID_RESTAURANT_ROLES = frozenset({"manager", "staff", "viewer"})
VALID_BRANCH_ROLES = frozenset({"branch_manager", "branch_staff"})
VALID_MEMBERSHIP_STATUSES = frozenset({"invited", "active", "suspended", "revoked"})


@dataclass(frozen=True, slots=True)
class OrganizationMembershipEntity:
    """Domain representation of a user's membership in an organization."""

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    status: str
    created_at: datetime
    updated_at: datetime
    joined_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.role not in VALID_ORG_ROLES:
            raise ValidationDomainError(f"Invalid organization role: '{self.role}'.")
        if self.status not in VALID_MEMBERSHIP_STATUSES:
            raise ValidationDomainError(f"Invalid membership status: '{self.status}'.")


@dataclass(frozen=True, slots=True)
class RestaurantMembershipEntity:
    """Domain representation of a user's restaurant-scoped role assignment."""

    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    user_id: UUID
    role: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.role not in VALID_RESTAURANT_ROLES:
            raise ValidationDomainError(f"Invalid restaurant role: '{self.role}'.")


@dataclass(frozen=True, slots=True)
class BranchAssignmentEntity:
    """Domain representation of a user's assignment to a specific restaurant branch."""

    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    branch_id: UUID
    user_id: UUID
    role: str
    status: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.role not in VALID_BRANCH_ROLES:
            raise ValidationDomainError(f"Invalid branch role: '{self.role}'.")
        if self.status not in VALID_MEMBERSHIP_STATUSES:
            raise ValidationDomainError(f"Invalid assignment status: '{self.status}'.")
