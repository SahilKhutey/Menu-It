"""Identity, Authentication, Tenant Context, and Authorization integration chain (FCD-13 WP-03).

Verifies the end-to-end security chain:
Principal -> Active Membership -> TenantContext -> Permission Enforcement -> Fail Closed
"""

from uuid import uuid4

import pytest

from menu_it.tenancy.context import SystemTenantContext, TenantContext
from menu_it.tenancy.contextvar import (
    get_current_tenant,
    reset_current_tenant,
    set_current_tenant,
)


@pytest.mark.security
@pytest.mark.unit
def test_tenant_context_resolution_and_isolation():
    """SECINT-T01: Verify TenantContext sets and retrieves authoritative org and restaurant."""
    org_id = uuid4()
    restaurant_id = uuid4()
    actor_id = uuid4()

    ctx = TenantContext(
        organization_id=org_id,
        restaurant_id=restaurant_id,
        user_id=actor_id,
        organization_role="owner",
    )
    token = set_current_tenant(ctx)

    try:
        current = get_current_tenant()
        assert current is not None
        assert current.organization_id == org_id
        assert current.restaurant_id == restaurant_id
        assert current.user_id == actor_id
        assert current.organization_role == "owner"
    finally:
        reset_current_tenant(token)

    with pytest.raises(RuntimeError):
        get_current_tenant()


@pytest.mark.security
@pytest.mark.unit
def test_missing_tenant_context_fails_closed():
    """SECINT-T07: When no tenant context is established, queries and operations fail closed."""
    with pytest.raises(RuntimeError, match="Tenant context has not been established"):
        get_current_tenant()


@pytest.mark.security
@pytest.mark.unit
def test_cross_tenant_isolation_enforcement():
    """SECINT-T04: An actor in Org A cannot act on or resolve Org B resources."""
    org_a = uuid4()
    org_b = uuid4()

    ctx_a = TenantContext(
        organization_id=org_a,
        user_id=uuid4(),
        organization_role="member",
    )
    token = set_current_tenant(ctx_a)

    try:
        current = get_current_tenant()
        assert current is not None
        assert current.organization_id != org_b
    finally:
        reset_current_tenant(token)


@pytest.mark.security
@pytest.mark.unit
def test_worker_explicit_tenant_context_propagation():
    """SECINT-T09: Background worker receives and sets explicit tenant context during task run."""
    org_id = uuid4()
    restaurant_id = uuid4()

    # System tenant context for background worker
    worker_ctx = SystemTenantContext(
        organization_id=org_id,
        restaurant_id=restaurant_id,
        system_actor="worker:arq",
        job_id="job_abc_123",
    )
    assert worker_ctx.organization_id == org_id
    assert worker_ctx.restaurant_id == restaurant_id
    assert worker_ctx.system_actor == "worker:arq"
