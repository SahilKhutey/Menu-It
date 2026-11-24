"""Authorization package initialization (FCD-05 §13, §14)."""

from menu_it.authorization.dependencies import (
    require_permission,
    require_platform_role,
)
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
from menu_it.authorization.policies import (
    ORGANIZATION_ROLE_PERMISSIONS,
    PLATFORM_ROLE_PERMISSIONS,
    RESTAURANT_ROLE_PERMISSIONS,
)
from menu_it.authorization.roles import (
    OrganizationRole,
    PlatformRole,
    RestaurantRole,
)

__all__ = [
    "ORGANIZATION_ROLE_PERMISSIONS",
    "PLATFORM_ROLE_PERMISSIONS",
    "Permission",
    "PermissionDeniedError",
    "OrganizationRole",
    "PlatformRole",
    "RESTAURANT_ROLE_PERMISSIONS",
    "RestaurantRole",
    "has_organization_permission",
    "has_platform_permission",
    "has_restaurant_permission",
    "require_organization_permission",
    "require_permission",
    "require_platform_permission",
    "require_platform_role",
    "require_restaurant_permission",
]
