"""Tenant-aware infrastructure naming and context interfaces (FCD-04 §17)."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.tenancy.context import TenantContext


@dataclass(frozen=True, slots=True)
class TenantJobContext:
    """Explicit tenant context carried by background workers (FCD-04 §17.4)."""

    organization_id: UUID
    actor_user_id: UUID | None
    job_id: str
    correlation_id: str


def format_tenant_storage_key(
    organization_id: UUID,
    resource_type: str,
    resource_id: str,
    restaurant_id: UUID | None = None,
) -> str:
    """Construct tenant-namespaced object storage key (FCD-04 §17.2).

    Pattern:
    organizations/{org_id}/restaurants/{restaurant_id}/{resource_type}/{resource_id}
    or organizations/{org_id}/{resource_type}/{resource_id}
    """
    if restaurant_id:
        return (
            f"organizations/{organization_id}/restaurants/{restaurant_id}/"
            f"{resource_type}/{resource_id}"
        )
    return f"organizations/{organization_id}/{resource_type}/{resource_id}"


def format_tenant_cache_key(
    organization_id: UUID,
    resource_type: str,
    key_suffix: str,
    restaurant_id: UUID | None = None,
) -> str:
    """Construct tenant-prefixed cache key preventing cross-tenant collisions (FCD-04 §17.3).

    Pattern:
    menu-it:org:{org_id}:rest:{restaurant_id}:{resource_type}:{key_suffix}
    or menu-it:org:{org_id}:{resource_type}:{key_suffix}
    """
    if restaurant_id:
        return f"menu-it:org:{organization_id}:rest:{restaurant_id}:{resource_type}:{key_suffix}"
    return f"menu-it:org:{organization_id}:{resource_type}:{key_suffix}"


async def record_audit_event(
    session: AsyncSession,
    context: TenantContext,
    *,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> OrganizationAuditEvent:
    """Record an append-only audit trail event bound to the active TenantContext."""
    event = OrganizationAuditEvent(
        organization_id=context.organization_id,
        actor_id=context.user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        correlation_id=context.correlation_id,
        metadata_=metadata or {},
    )
    session.add(event)
    await session.flush()
    return event
