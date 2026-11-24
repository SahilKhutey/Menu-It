"""Organization endpoints utilizing tenant dependencies (FCD-04 §10.2)."""

import contextlib
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from menu_it.authorization.dependencies import require_permission
from menu_it.authorization.permissions import Permission
from menu_it.authorization.policies import ORGANIZATION_ROLE_PERMISSIONS
from menu_it.schemas.common import APIResponse, ResponseMetadata
from menu_it.tenancy.context import TenantContext
from menu_it.tenancy.dependencies import get_tenant_context

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get(
    "/{organization_id}/current",
    response_model=APIResponse[dict[str, str | None]],
    summary="Get Resolved Tenant Context",
)
async def get_current_organization(
    tenant: Annotated[TenantContext, Depends(get_tenant_context)],
) -> APIResponse[dict[str, str | None]]:
    """Return active organization tenant context derived from trusted membership."""
    req_id = UUID(int=0)
    if tenant.correlation_id:
        try:
            req_id = UUID(tenant.correlation_id)
        except ValueError:
            req_id = UUID(int=0)

    return APIResponse(
        success=True,
        data={
            "organization_id": str(tenant.organization_id),
            "user_id": str(tenant.user_id),
            "organization_role": tenant.organization_role,
            "restaurant_id": str(tenant.restaurant_id) if tenant.restaurant_id else None,
            "restaurant_role": tenant.restaurant_role,
        },
        meta=ResponseMetadata(
            request_id=req_id,
        ),
    )


@router.get(
    "/{organization_id}/access",
    response_model=APIResponse[dict[str, object]],
    summary="Get Authorized Organization Access Summary",
)
async def get_organization_access_summary(
    tenant: Annotated[
        TenantContext,
        Depends(require_permission(Permission.ORGANIZATION_READ)),
    ],
) -> APIResponse[dict[str, object]]:
    """Return verified permissions and roles within the authorized organization (FCD-05 §18.1)."""
    permissions = [
        p.value for p in ORGANIZATION_ROLE_PERMISSIONS.get(tenant.organization_role, set())
    ]
    req_id = UUID(int=0)
    if tenant.correlation_id:
        with contextlib.suppress(ValueError):
            req_id = UUID(tenant.correlation_id)

    return APIResponse(
        success=True,
        data={
            "organization_id": str(tenant.organization_id),
            "user_id": str(tenant.user_id),
            "organization_role": tenant.organization_role,
            "restaurant_id": str(tenant.restaurant_id) if tenant.restaurant_id else None,
            "restaurant_role": tenant.restaurant_role,
            "permissions": sorted(permissions),
        },
        meta=ResponseMetadata(request_id=req_id),
    )
