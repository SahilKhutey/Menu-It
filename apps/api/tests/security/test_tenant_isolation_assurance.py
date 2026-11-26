"""Tests for tenant isolation and authorization boundary enforcement (FCD-11 WP-03 / WP-04)."""

import uuid

import pytest

from menu_it.platform.security.authorization import (
    PermissionDeniedError,
    TenantAccessDeniedError,
    assert_tenant_boundary,
    require_permission,
)


def test_assert_tenant_boundary_matching_tenants_pass() -> None:
    org_id = uuid.uuid4()
    # Matching resource and context IDs should not raise
    assert_tenant_boundary(org_id, org_id)


def test_assert_tenant_boundary_mismatch_raises() -> None:
    org_1 = uuid.uuid4()
    org_2 = uuid.uuid4()
    with pytest.raises(TenantAccessDeniedError) as exc:
        assert_tenant_boundary(org_1, org_2)

    assert str(org_1) in str(exc.value)
    assert str(org_2) in str(exc.value)


def test_assert_tenant_boundary_unscoped_resource() -> None:
    context_org = uuid.uuid4()

    # Disallowed unscoped resource
    with pytest.raises(TenantAccessDeniedError):
        assert_tenant_boundary(None, context_org, allow_unscoped_resource=False)

    # Allowed unscoped resource
    assert_tenant_boundary(None, context_org, allow_unscoped_resource=True)


def test_require_permission_exact_match() -> None:
    perms = {"restaurant:read", "restaurant:write"}
    require_permission(perms, "restaurant:read")


def test_require_permission_super_wildcard() -> None:
    require_permission({"*"}, "any:arbitrary:action")
    require_permission({"admin"}, "finance:audit")


def test_require_permission_domain_wildcard() -> None:
    require_permission({"menu:*"}, "menu:item:create")
    require_permission({"menu:*"}, "menu:category:delete")


def test_require_permission_missing_raises() -> None:
    with pytest.raises(PermissionDeniedError):
        require_permission({"restaurant:read"}, "restaurant:delete")
