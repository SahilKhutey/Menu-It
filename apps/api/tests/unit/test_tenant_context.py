"""Unit tests for immutable TenantContext and infrastructure helpers (FCD-04 §8, §17)."""

from uuid import uuid4

import pytest

from menu_it.tenancy.context import SystemTenantContext, TenantContext
from menu_it.tenancy.contextvar import (
    get_current_tenant,
    reset_current_tenant,
    set_current_tenant,
)
from menu_it.tenancy.infrastructure import (
    TenantJobContext,
    format_tenant_cache_key,
    format_tenant_storage_key,
)


def test_context_is_immutable():
    """Verify TenantContext fields cannot be altered after instantiation."""
    context = TenantContext(
        organization_id=uuid4(),
        user_id=uuid4(),
        organization_role="owner",
    )
    with pytest.raises(AttributeError):
        context.organization_role = "viewer"  # type: ignore[misc]


def test_restaurant_scope_is_optional():
    """Verify TenantContext defaults restaurant fields to None for org-level operations."""
    org_id = uuid4()
    user_id = uuid4()
    context = TenantContext(
        organization_id=org_id,
        user_id=user_id,
        organization_role="admin",
    )
    assert context.organization_id == org_id
    assert context.user_id == user_id
    assert context.organization_role == "admin"
    assert context.restaurant_id is None
    assert context.restaurant_role is None
    assert context.correlation_id is None


def test_contextvar_lifecycle():
    """Verify ContextVar set, get, and reset lifecycle with token cleanup."""
    context = TenantContext(
        organization_id=uuid4(),
        user_id=uuid4(),
        organization_role="owner",
    )

    token = set_current_tenant(context)
    assert get_current_tenant() == context

    reset_current_tenant(token)
    with pytest.raises(RuntimeError) as exc_info:
        get_current_tenant()
    assert "Tenant context has not been established" in str(exc_info.value)


def test_infrastructure_keys():
    """Verify tenant-namespaced object storage and cache key conventions (FCD-04 §17.2, §17.3)."""
    org_id = uuid4()
    rest_id = uuid4()

    # Storage key formatting
    storage_key_org = format_tenant_storage_key(org_id, "logos", "logo.png")
    assert storage_key_org == f"organizations/{org_id}/logos/logo.png"

    storage_key_rest = format_tenant_storage_key(org_id, "menus", "menu.pdf", restaurant_id=rest_id)
    assert storage_key_rest == f"organizations/{org_id}/restaurants/{rest_id}/menus/menu.pdf"

    # Cache key formatting
    cache_key_org = format_tenant_cache_key(org_id, "settings", "theme")
    assert cache_key_org == f"menu-it:org:{org_id}:settings:theme"

    cache_key_rest = format_tenant_cache_key(org_id, "menus", "snapshot-v1", restaurant_id=rest_id)
    assert cache_key_rest == f"menu-it:org:{org_id}:rest:{rest_id}:menus:snapshot-v1"


def test_system_and_job_context():
    """Verify system context and background job context interfaces."""
    org_id = uuid4()
    actor_id = uuid4()

    job_ctx = TenantJobContext(
        organization_id=org_id,
        actor_user_id=actor_id,
        job_id="job-999",
        correlation_id="req-123",
    )
    assert job_ctx.organization_id == org_id
    assert job_ctx.actor_user_id == actor_id

    sys_ctx = SystemTenantContext(
        organization_id=org_id,
        system_actor="report-worker",
        job_id="cron-001",
    )
    assert sys_ctx.organization_id == org_id
    assert sys_ctx.system_actor == "report-worker"
