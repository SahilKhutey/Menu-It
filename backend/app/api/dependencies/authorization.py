"""
ModularMenu — API Authorization Dependencies (ARC-07 §6.4, §6.5).
Evaluates fine-grained permissions against the server-derived TenantContext.
"""
from typing import Callable
from fastapi import Depends, HTTPException, status

from app.api.dependencies.tenant import get_tenant_context
from app.shared.application.authorization import DEFAULT_ROLE_PERMISSIONS
from app.shared.application.tenant_context import TenantContext
from app.shared.domain.permissions import Permission


def require_permission(permission_str: str) -> Callable:
    """
    Factory creating a FastAPI dependency that verifies whether the authenticated
    actor holds the specified permission within their active TenantContext.
    """
    async def permission_checker(
        tenant: TenantContext = Depends(get_tenant_context),
    ) -> TenantContext:
        role = tenant.organization_role.lower()
        role_permissions = DEFAULT_ROLE_PERMISSIONS.get(role, frozenset())

        # Normalize common permission aliases
        effective_perm = permission_str
        aliases = {
            "item.manage": "food_item.manage",
            "editor.read": "editor.draft.read",
            "editor.write": "editor.draft.write",
        }
        effective_perm = aliases.get(permission_str, permission_str)

        # Match either exact Permission enum value or string representation
        has_perm = any(
            p.value == effective_perm or str(p) == effective_perm or p.value == permission_str
            for p in role_permissions
        )

        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: Missing required permission '{permission_str}'",
            )

        return tenant

    return permission_checker
