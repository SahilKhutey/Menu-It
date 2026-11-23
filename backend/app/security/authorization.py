"""
ModularMenu — Central Authorization Engine & RBAC (ARC-12 §5, ADR-0227).
Granular resource-level and tenant-scoped permission enforcement.
"""

from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, status

# Granular permission definitions (ARC-12 §5.3)
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "platform_owner": frozenset(
        {
            "platform.users.manage",
            "platform.tenants.manage",
            "platform.audit.read",
            "organization.read",
            "organization.update",
            "organization.members.manage",
            "restaurant.read",
            "restaurant.update",
            "restaurant.settings.manage",
            "menu.read",
            "menu.create",
            "menu.update",
            "menu.delete",
            "menu.validate",
            "menu.publish",
            "menu.rollback",
            "theme.read",
            "theme.configure",
            "media.upload",
            "media.read",
            "media.delete",
            "publication.read",
            "publication.audit.read",
        }
    ),
    "restaurant_owner": frozenset(
        {
            "organization.read",
            "organization.update",
            "organization.members.manage",
            "restaurant.read",
            "restaurant.update",
            "restaurant.settings.manage",
            "menu.read",
            "menu.create",
            "menu.update",
            "menu.delete",
            "menu.validate",
            "menu.publish",
            "menu.rollback",
            "theme.read",
            "theme.configure",
            "media.upload",
            "media.read",
            "media.delete",
            "publication.read",
            "publication.audit.read",
            "subscription.read",
            "subscription.manage",
        }
    ),
    "restaurant_manager": frozenset(
        {
            "organization.read",
            "restaurant.read",
            "restaurant.update",
            "restaurant.settings.manage",
            "menu.read",
            "menu.create",
            "menu.update",
            "menu.delete",
            "menu.validate",
            "menu.publish",
            "menu.rollback",
            "theme.read",
            "theme.configure",
            "media.upload",
            "media.read",
            "publication.read",
            "publication.audit.read",
        }
    ),
    "menu_editor": frozenset(
        {
            "organization.read",
            "restaurant.read",
            "menu.read",
            "menu.create",
            "menu.update",
            "menu.validate",
            "theme.read",
            "media.upload",
            "media.read",
            "publication.read",
        }
    ),
    "viewer": frozenset(
        {
            "organization.read",
            "restaurant.read",
            "menu.read",
            "theme.read",
            "media.read",
            "publication.read",
        }
    ),
}


@dataclass(frozen=True)
class AuthorizationContext:
    """Enforceable context resolving who the actor is and what they may access."""

    user_id: UUID
    organization_id: UUID
    role: str
    permissions: frozenset[str]
    allowed_restaurant_ids: frozenset[UUID] | None = None
    is_support_access: bool = False

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def can_access_restaurant(self, restaurant_id: UUID) -> bool:
        if self.allowed_restaurant_ids is None:
            return True
        return restaurant_id in self.allowed_restaurant_ids


def require_permission(context: AuthorizationContext, permission: str) -> None:
    """Enforce permission check; raises HTTP 403 Forbidden on failure."""
    if not context.has_permission(permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: missing required permission '{permission}'",
        )


def require_restaurant_access(context: AuthorizationContext, restaurant_id: UUID) -> None:
    """Enforce restaurant scoping; raises HTTP 403 Forbidden if not in allowed scope."""
    if not context.can_access_restaurant(restaurant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: outside allocated restaurant scope",
        )
