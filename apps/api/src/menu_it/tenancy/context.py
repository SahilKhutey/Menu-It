"""Immutable tenant context model (FCD-04 §8.1)."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Immutable server-side tenant and user context for an operation.

    Attributes:
        organization_id: Canonical primary tenant organization UUID.
        user_id: Authenticated principal user UUID.
        organization_role: Role held within the organization (e.g. owner, admin).
        restaurant_id: Optional restaurant location UUID if restaurant-scoped.
        restaurant_role: Optional role within the restaurant if assigned.
        correlation_id: Request correlation tracking ID (e.g. X-Request-ID).
    """

    organization_id: UUID
    user_id: UUID
    organization_role: str
    restaurant_id: UUID | None = None
    restaurant_role: str | None = None
    correlation_id: str | None = None


@dataclass(frozen=True, slots=True)
class SystemTenantContext:
    """Tenant context for asynchronous system or background jobs (FCD-04 §8.1)."""

    organization_id: UUID
    system_actor: str
    job_id: str
    restaurant_id: UUID | None = None
    correlation_id: str | None = None
