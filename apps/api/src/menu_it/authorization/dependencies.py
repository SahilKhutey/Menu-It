"""FastAPI authorization dependencies for tenant and platform permission gating (FCD-05 §14.4)."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.auth.dependencies import get_current_principal
from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.authorization.evaluator import (
    PermissionDeniedError,
    require_organization_permission,
    require_restaurant_permission,
)
from menu_it.authorization.permissions import Permission
from menu_it.database.models.platform import (
    PlatformMembership,
    PlatformMembershipStatus,
    PlatformRole,
)
from menu_it.database.session import get_db_session
from menu_it.tenancy.context import TenantContext
from menu_it.tenancy.dependencies import get_tenant_context


def require_permission(
    permission: Permission,
) -> Callable[[TenantContext], TenantContext]:
    """Dependency factory enforcing organization or restaurant-level permissions.

    Evaluates active organization role from the server-resolved TenantContext.
    If the operation is restaurant-scoped and an assignment role exists, falls back
    to restaurant permissions.
    """

    async def _dependency(
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ) -> TenantContext:
        # Check organization authority
        try:
            require_organization_permission(tenant.organization_role, permission)
            return tenant
        except PermissionDeniedError:
            pass

        # If scoped to a specific restaurant and user has a restaurant assignment, evaluate it
        if tenant.restaurant_id and tenant.restaurant_role:
            try:
                require_restaurant_permission(tenant.restaurant_role, permission)
                return tenant
            except PermissionDeniedError:
                pass

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions: requires '{permission}'.",
        )

    return _dependency


def require_platform_role(
    *allowed_roles: PlatformRole,
) -> Callable[..., PlatformMembership]:
    """Dependency factory enforcing isolated platform-level administration privileges."""

    async def _platform_dependency(
        principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> PlatformMembership:
        statement = select(PlatformMembership).where(
            PlatformMembership.user_id == principal.user_id,
            PlatformMembership.status == PlatformMembershipStatus.ACTIVE,
        )
        result = await session.execute(statement)
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Platform administrative privilege required.",
            )

        if allowed_roles and membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{membership.role}' lacks required platform authority.",
            )

        return membership

    return _platform_dependency
