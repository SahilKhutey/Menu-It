"""
ModularMenu — Authorization Policy and Decision Engine (ARC-05 §5.4, §5.6).
Evaluates server-derived TenantContext against role permissions and branch boundaries.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from uuid import UUID

from app.shared.application.tenant_context import TenantContext
from app.shared.domain.permissions import Permission
from app.shared.domain.tenant_exceptions import TenantAccessDeniedException

DEFAULT_ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "owner": frozenset(Permission),
    "org_admin": frozenset(p for p in Permission if p != Permission.ORGANIZATION_DELETE),
    "admin": frozenset(p for p in Permission if p != Permission.ORGANIZATION_DELETE),
    "restaurant_manager": frozenset(
        {
            Permission.RESTAURANT_READ,
            Permission.RESTAURANT_UPDATE,
            Permission.MENU_CREATE,
            Permission.MENU_READ,
            Permission.MENU_UPDATE,
            Permission.MENU_DELETE,
            Permission.MENU_PUBLISH,
            Permission.MENU_ROLLBACK,
            Permission.CATEGORY_MANAGE,
            Permission.FOOD_ITEM_MANAGE,
            Permission.PRICING_MANAGE,
            Permission.AVAILABILITY_MANAGE,
            Permission.THEME_READ,
            Permission.THEME_UPDATE,
            Permission.LAYOUT_UPDATE,
            Permission.EDITOR_DRAFT_READ,
            Permission.EDITOR_DRAFT_WRITE,
            Permission.MEDIA_UPLOAD,
            Permission.MEDIA_READ_PRIVATE,
            Permission.SUBSCRIPTION_READ,
        }
    ),
    "manager": frozenset(
        {
            Permission.RESTAURANT_READ,
            Permission.RESTAURANT_UPDATE,
            Permission.MENU_CREATE,
            Permission.MENU_READ,
            Permission.MENU_UPDATE,
            Permission.MENU_DELETE,
            Permission.MENU_PUBLISH,
            Permission.MENU_ROLLBACK,
            Permission.CATEGORY_MANAGE,
            Permission.FOOD_ITEM_MANAGE,
            Permission.PRICING_MANAGE,
            Permission.AVAILABILITY_MANAGE,
            Permission.THEME_READ,
            Permission.THEME_UPDATE,
            Permission.LAYOUT_UPDATE,
            Permission.EDITOR_DRAFT_READ,
            Permission.EDITOR_DRAFT_WRITE,
            Permission.MEDIA_UPLOAD,
            Permission.MEDIA_READ_PRIVATE,
            Permission.SUBSCRIPTION_READ,
        }
    ),
    "menu_editor": frozenset(
        {
            Permission.RESTAURANT_READ,
            Permission.MENU_READ,
            Permission.MENU_UPDATE,
            Permission.CATEGORY_MANAGE,
            Permission.FOOD_ITEM_MANAGE,
            Permission.THEME_READ,
            Permission.THEME_UPDATE,
            Permission.LAYOUT_UPDATE,
            Permission.EDITOR_DRAFT_READ,
            Permission.EDITOR_DRAFT_WRITE,
            Permission.MEDIA_UPLOAD,
            Permission.MEDIA_READ_PRIVATE,
        }
    ),
    "editor": frozenset(
        {
            Permission.RESTAURANT_READ,
            Permission.MENU_READ,
            Permission.MENU_UPDATE,
            Permission.CATEGORY_MANAGE,
            Permission.FOOD_ITEM_MANAGE,
            Permission.THEME_READ,
            Permission.THEME_UPDATE,
            Permission.LAYOUT_UPDATE,
            Permission.EDITOR_DRAFT_READ,
            Permission.EDITOR_DRAFT_WRITE,
            Permission.MEDIA_UPLOAD,
            Permission.MEDIA_READ_PRIVATE,
        }
    ),
    "viewer": frozenset(
        {
            Permission.ORGANIZATION_READ,
            Permission.RESTAURANT_READ,
            Permission.MENU_READ,
            Permission.THEME_READ,
            Permission.SUBSCRIPTION_READ,
        }
    ),
}


@dataclass(frozen=True)
class AuthorizationPolicy:
    """
    Evaluates fine-grained permissions and branch scoping against an immutable TenantContext.
    """

    role_permissions: Mapping[str, frozenset[Permission]] = field(
        default_factory=lambda: DEFAULT_ROLE_PERMISSIONS
    )

    def is_allowed(
        self,
        context: TenantContext,
        permission: Permission,
        restaurant_id: UUID | None = None,
    ) -> bool:
        """Non-raising permission inquiry."""
        role_key = context.organization_role.lower()
        allowed_perms = self.role_permissions.get(role_key, frozenset())
        if permission not in allowed_perms:
            return False

        if restaurant_id is not None:
            if not context.has_restaurant_access(restaurant_id):
                return False

        return True

    def require(
        self,
        context: TenantContext,
        permission: Permission,
        restaurant_id: UUID | None = None,
    ) -> None:
        """
        Enforces permission and branch boundaries.
        Raises TenantAccessDeniedException if check fails.
        """
        role_key = context.organization_role.lower()
        allowed_perms = self.role_permissions.get(role_key, frozenset())
        if permission not in allowed_perms:
            raise TenantAccessDeniedException(
                f"Role '{context.organization_role}' lacks required permission '{permission.value}'"
            )

        if restaurant_id is not None:
            if not context.has_restaurant_access(restaurant_id):
                raise TenantAccessDeniedException(
                    f"Context lacks access to restaurant branch '{restaurant_id}'"
                )
