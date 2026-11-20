"""
ModularMenu — Tenant Context (ARC-05 §4.1, ARC05-D06).
Immutable, request-scoped context derived strictly by server-side authentication
and active organization membership resolution.
"""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class TenantContext:
    """
    Authoritative, server-derived tenant execution context.
    Must NEVER be deserialized directly from client-supplied request payloads.
    """
    user_id: UUID
    organization_id: UUID
    membership_id: UUID
    organization_role: str
    allowed_restaurant_ids: Optional[frozenset[UUID]] = None
    request_id: str = ""
    authentication_method: str = "session"

    def __post_init__(self) -> None:
        if not self.user_id:
            raise ValueError("user_id must be a non-null UUID")
        if not self.organization_id:
            raise ValueError("organization_id must be a non-null UUID")
        if not self.membership_id:
            raise ValueError("membership_id must be a non-null UUID")
        if not self.organization_role:
            raise ValueError("organization_role must be specified")

    def has_restaurant_access(self, restaurant_id: UUID) -> bool:
        """
        Validates whether the context allows access to a specific restaurant.
        If allowed_restaurant_ids is None, user has organization-wide branch access.
        Otherwise, restaurant_id must be explicitly present in allowed_restaurant_ids.
        """
        if self.allowed_restaurant_ids is None:
            return True
        return restaurant_id in self.allowed_restaurant_ids

    @property
    def is_owner(self) -> bool:
        return self.organization_role.lower() == "owner"

    @property
    def is_admin(self) -> bool:
        return self.organization_role.lower() in ("owner", "admin", "org_admin")
