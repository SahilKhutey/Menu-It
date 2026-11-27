"""Unit tests for role-to-permission policy evaluation matrices (FCD-05 §21.7)."""

import pytest

from menu_it.authorization.evaluator import (
    PermissionDeniedError,
    has_organization_permission,
    has_platform_permission,
    has_restaurant_permission,
    require_organization_permission,
    require_platform_permission,
    require_restaurant_permission,
)
from menu_it.authorization.permissions import Permission
from menu_it.database.models.organization_membership import OrganizationRole
from menu_it.database.models.platform import PlatformRole
from menu_it.database.models.restaurant_membership import RestaurantRole


def test_owner_permissions():
    """Verify OWNER role possesses full organization and administrative permissions."""
    assert has_organization_permission(OrganizationRole.OWNER, Permission.ORGANIZATION_READ)
    assert has_organization_permission(
        OrganizationRole.OWNER, Permission.ORGANIZATION_MANAGE_MEMBERS
    )
    assert has_organization_permission(OrganizationRole.OWNER, Permission.MENU_PUBLISH)
    assert has_organization_permission(OrganizationRole.OWNER, Permission.BILLING_MANAGE)
    require_organization_permission(OrganizationRole.OWNER, Permission.ORDER_CANCEL)


def test_admin_permissions():
    """Verify ADMIN role possesses operational authority."""
    assert has_organization_permission(
        OrganizationRole.ADMIN, Permission.ORGANIZATION_MANAGE_MEMBERS
    )
    assert has_organization_permission(OrganizationRole.ADMIN, Permission.RESTAURANT_CREATE)
    assert has_organization_permission(OrganizationRole.ADMIN, Permission.MENU_PUBLISH)


def test_manager_permissions():
    """Verify MANAGER role can manage menus and orders but cannot manage members or billing."""
    assert has_organization_permission(OrganizationRole.MANAGER, Permission.MENU_PUBLISH)
    assert has_organization_permission(OrganizationRole.MANAGER, Permission.ORDER_CANCEL)
    assert not has_organization_permission(
        OrganizationRole.MANAGER, Permission.ORGANIZATION_MANAGE_MEMBERS
    )
    assert not has_organization_permission(OrganizationRole.MANAGER, Permission.BILLING_MANAGE)


def test_staff_permissions():
    """Verify STAFF role can view and update orders but cannot publish menus or manage billing."""
    assert has_organization_permission(OrganizationRole.STAFF, Permission.ORDER_READ)
    assert has_organization_permission(OrganizationRole.STAFF, Permission.ORDER_UPDATE)
    assert not has_organization_permission(OrganizationRole.STAFF, Permission.MENU_PUBLISH)
    assert not has_organization_permission(OrganizationRole.STAFF, Permission.BILLING_MANAGE)


def test_viewer_permissions():
    """Verify VIEWER role possesses strictly read-only visibility."""
    assert has_organization_permission(OrganizationRole.VIEWER, Permission.MENU_READ)
    assert has_organization_permission(OrganizationRole.VIEWER, Permission.ORGANIZATION_READ)
    assert not has_organization_permission(OrganizationRole.VIEWER, Permission.ORDER_CREATE)
    assert not has_organization_permission(OrganizationRole.VIEWER, Permission.MENU_PUBLISH)


def test_unknown_role_denied():
    """Verify unknown or unassigned roles are rejected (deny by default)."""
    assert not has_organization_permission("anonymous", Permission.MENU_READ)
    assert not has_organization_permission("random_role", Permission.ORGANIZATION_READ)
    with pytest.raises(PermissionDeniedError, match="lacks required permission"):
        require_organization_permission("anonymous", Permission.MENU_READ)


def test_restaurant_roles():
    """Verify fine-grained restaurant-level roles."""
    assert has_restaurant_permission(RestaurantRole.MANAGER, Permission.MENU_PUBLISH)
    assert has_restaurant_permission(RestaurantRole.STAFF, Permission.ORDER_CREATE)
    assert not has_restaurant_permission(RestaurantRole.STAFF, Permission.MENU_PUBLISH)
    assert not has_restaurant_permission(RestaurantRole.VIEWER, Permission.ORDER_CREATE)

    require_restaurant_permission(RestaurantRole.MANAGER, Permission.RESTAURANT_UPDATE)
    with pytest.raises(PermissionDeniedError):
        require_restaurant_permission(RestaurantRole.STAFF, Permission.RESTAURANT_UPDATE)


def test_platform_roles():
    """Verify platform-level privilege boundaries."""
    assert has_platform_permission(
        PlatformRole.PLATFORM_ADMIN, Permission.PLATFORM_MANAGE_ORGANIZATIONS
    )
    assert has_platform_permission(PlatformRole.PLATFORM_ADMIN, Permission.PLATFORM_MANAGE_USERS)
    assert has_platform_permission(
        PlatformRole.PLATFORM_SUPPORT, Permission.PLATFORM_MANAGE_SUPPORT_ACCESS
    )
    assert not has_platform_permission(
        PlatformRole.PLATFORM_SUPPORT, Permission.PLATFORM_MANAGE_USERS
    )
    assert has_platform_permission(
        PlatformRole.PLATFORM_OPERATOR, Permission.PLATFORM_VIEW_AUDIT_LOGS
    )

    require_platform_permission(PlatformRole.PLATFORM_ADMIN, Permission.PLATFORM_MANAGE_USERS)
    with pytest.raises(PermissionDeniedError):
        require_platform_permission(PlatformRole.PLATFORM_SUPPORT, Permission.PLATFORM_MANAGE_USERS)
