"""Permission evaluation dependencies for API endpoints (FCD-07 §12.2)."""

from menu_it.authorization.dependencies import (
    require_permission,
    require_platform_role,
)
from menu_it.authorization.permissions import Permission

__all__ = [
    "Permission",
    "require_permission",
    "require_platform_role",
]
