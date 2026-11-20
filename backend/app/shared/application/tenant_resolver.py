"""
ModularMenu — Tenant Context Resolver (ARC-05 §4.2, §4.3).
Authoritative, server-side resolution of TenantContext from authenticated user sessions
and validated organization memberships.
"""
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence
from uuid import UUID

from app.shared.application.tenant_context import TenantContext
from app.shared.domain.tenant_exceptions import (
    CrossTenantAccessException,
    InvalidTenantContextException,
    TenantAccessDeniedException,
    TenantSuspendedException,
)


@dataclass(frozen=True)
class MembershipRecord:
    """Read model of an organization membership."""
    membership_id: UUID
    user_id: UUID
    organization_id: UUID
    role: str
    is_active: bool
    allowed_restaurant_ids: Optional[frozenset[UUID]] = None


@dataclass(frozen=True)
class OrganizationStatus:
    """Read model of organization status."""
    organization_id: UUID
    status: str  # 'active', 'suspended', 'offboarded'


class TenantResolver:
    """
    Authoritative server-side resolver that guarantees client-supplied tenant IDs
    are treated strictly as selectors, never as proof of access.
    """
    def __init__(
        self,
        membership_provider: Mapping[tuple[UUID, UUID], MembershipRecord] | None = None,
        org_status_provider: Mapping[UUID, str] | None = None,
    ):
        self._memberships = dict(membership_provider or {})
        self._org_statuses = dict(org_status_provider or {})

    def register_membership(self, record: MembershipRecord) -> None:
        self._memberships[(record.user_id, record.organization_id)] = record

    def set_organization_status(self, organization_id: UUID, status: str) -> None:
        self._org_statuses[organization_id] = status

    def resolve(
        self,
        user_id: Optional[UUID],
        target_organization_id: Optional[UUID],
        request_id: str = "",
        authentication_method: str = "bearer_jwt",
        allow_suspended: bool = False,
    ) -> TenantContext:
        """
        Resolves and validates a TenantContext.
        Fails closed on any invalid, missing, or unauthorized tenant selector.
        """
        if not user_id:
            raise InvalidTenantContextException("Cannot resolve tenant for unauthenticated user")
        if not target_organization_id:
            raise InvalidTenantContextException("Target organization ID must be provided")

        membership = self._memberships.get((user_id, target_organization_id))
        if not membership:
            # Client submitted forged or unauthorized organization ID
            raise CrossTenantAccessException(
                f"User '{user_id}' does not have active membership in organization '{target_organization_id}'"
            )

        if not membership.is_active:
            raise TenantAccessDeniedException(
                f"Membership for user '{user_id}' in organization '{target_organization_id}' is revoked or inactive"
            )

        org_status = self._org_statuses.get(target_organization_id, "active")
        if org_status == "suspended" and not allow_suspended:
            raise TenantSuspendedException(
                f"Organization '{target_organization_id}' is currently suspended"
            )
        elif org_status == "offboarded":
            raise TenantAccessDeniedException(
                f"Organization '{target_organization_id}' is offboarded and inaccessible"
            )

        return TenantContext(
            user_id=user_id,
            organization_id=target_organization_id,
            membership_id=membership.membership_id,
            organization_role=membership.role,
            allowed_restaurant_ids=membership.allowed_restaurant_ids,
            request_id=request_id,
            authentication_method=authentication_method,
        )
