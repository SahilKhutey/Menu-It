"""Authorization policy evaluation engine (FCD-05 §14.3)."""

from menu_it.authorization.permissions import Permission
from menu_it.authorization.policies import (
    ORGANIZATION_ROLE_PERMISSIONS,
    PLATFORM_ROLE_PERMISSIONS,
    RESTAURANT_ROLE_PERMISSIONS,
)


class PermissionDeniedError(Exception):
    """Raised when an actor lacks the necessary permission for an operation."""


def has_organization_permission(role: str, permission: Permission) -> bool:
    """Check if an organization role grants a specific permission."""
    allowed = ORGANIZATION_ROLE_PERMISSIONS.get(role)
    if allowed is None:
        return False
    return permission in allowed


def require_organization_permission(role: str, permission: Permission) -> None:
    """Assert an organization role holds the required permission."""
    if not has_organization_permission(role, permission):
        raise PermissionDeniedError(f"Role '{role}' lacks required permission '{permission}'.")


def has_restaurant_permission(role: str, permission: Permission) -> bool:
    """Check if a restaurant assignment role grants a specific permission."""
    allowed = RESTAURANT_ROLE_PERMISSIONS.get(role)
    if allowed is None:
        return False
    return permission in allowed


def require_restaurant_permission(role: str, permission: Permission) -> None:
    """Assert a restaurant role holds the required permission."""
    if not has_restaurant_permission(role, permission):
        raise PermissionDeniedError(
            f"Restaurant role '{role}' lacks required permission '{permission}'."
        )


def has_platform_permission(role: str, permission: Permission) -> bool:
    """Check if a platform role grants a platform permission."""
    allowed = PLATFORM_ROLE_PERMISSIONS.get(role)
    if allowed is None:
        return False
    return permission in allowed


def require_platform_permission(role: str, permission: Permission) -> None:
    """Assert a platform role holds the required platform permission."""
    if not has_platform_permission(role, permission):
        raise PermissionDeniedError(
            f"Platform role '{role}' lacks required permission '{permission}'."
        )
