"""
ModularMenu — Server-Derived Tenant Context Dependency (ARC-07 §6.3, ARC-05 §4.1).
Resolves and validates immutable TenantContext from server session and active memberships.
Rejects client-forged tenant IDs and enforces fail-closed semantics.
"""

from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authentication import AuthenticatedActor, get_current_actor
from app.core.database import get_db
from app.shared.application.tenant_context import TenantContext


async def get_tenant_context(
    request: Request,
    actor: AuthenticatedActor = Depends(get_current_actor),
    x_organization_id: str | None = Header(None, alias="X-Organization-ID"),
    db: AsyncSession = Depends(get_db),
) -> TenantContext:
    """
    Derives trusted, immutable TenantContext for the request (ARC-07 §6.3).
    """
    org_id_str = x_organization_id
    # Check path params if organization_id is in route
    if not org_id_str and "organization_id" in request.path_params:
        org_id_str = str(request.path_params["organization_id"])

    # Fallback to default user organization if omitted
    target_org_id: UUID | None = None
    if org_id_str:
        try:
            target_org_id = UUID(org_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed organization identifier",
            )

    # 1. Platform Admin bypass for administration
    if actor.is_platform_admin:
        org_id = target_org_id or UUID("00000000-0000-0000-0000-000000000000")
        return TenantContext(
            user_id=actor.user_id,
            organization_id=org_id,
            membership_id=actor.user_id,
            organization_role="owner",
            allowed_restaurant_ids=None,
            request_id=getattr(request.state, "request_id", ""),
            authentication_method="session",
        )

    # 2. Query Active Membership from identity model
    from app.modules.identity.models import RestaurantMember

    query = select(RestaurantMember).where(
        RestaurantMember.user_id == actor.user_id,
    )
    if target_org_id:
        query = query.where(RestaurantMember.organization_id == target_org_id)

    result = await db.execute(query)
    membership = result.scalars().first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have active membership in this organization tenant.",
        )

    # 3. Check restaurant assignment if restaurant_id in path
    allowed_restaurants = None
    if "restaurant_id" in request.path_params:
        try:
            rest_id = UUID(str(request.path_params["restaurant_id"]))
        except ValueError:
            raise HTTPException(status_code=400, detail="Malformed restaurant identifier")

        # If role is not owner/admin/org_admin, verify restaurant membership
        if membership.role.lower() not in ("owner", "admin", "org_admin"):
            rm_stmt = select(RestaurantMember).where(
                RestaurantMember.organization_id == membership.organization_id,
                RestaurantMember.restaurant_id == rest_id,
                RestaurantMember.user_id == actor.user_id,
            )
            rm_result = await db.execute(rm_stmt)
            if not rm_result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You are not assigned to this restaurant branch.",
                )

    return TenantContext(
        user_id=actor.user_id,
        organization_id=membership.organization_id,
        membership_id=membership.id,
        organization_role=membership.role,
        allowed_restaurant_ids=allowed_restaurants,
        request_id=getattr(request.state, "request_id", ""),
        authentication_method="session",
    )
