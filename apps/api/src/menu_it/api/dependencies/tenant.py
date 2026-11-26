"""Tenant context dependencies for API endpoints (FCD-07 §12.2)."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.auth.dependencies import get_current_principal
from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.database.session import get_db_session
from menu_it.tenancy.context import TenantContext
from menu_it.tenancy.dependencies import (
    get_restaurant_tenant_context,
    get_tenant_context,
)
from menu_it.tenancy.exceptions import (
    RestaurantAccessDeniedError,
    TenantAccessDeniedError,
    TenantNotFoundError,
    TenantSuspendedError,
)
from menu_it.tenancy.resolver import TenantResolver


def get_requested_organization_id(
    organization_id: Annotated[
        UUID | None,
        Query(description="Target tenant organization ID"),
    ] = None,
    x_organization_id: Annotated[
        UUID | None,
        Header(alias="X-Organization-ID", description="Target tenant organization ID header"),
    ] = None,
) -> UUID:
    """Resolve target organization ID from query parameter or request header."""
    resolved = organization_id or x_organization_id
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Organization identity required via query parameter "
                "'organization_id' or 'X-Organization-ID' header."
            ),
        )
    return resolved


def get_optional_organization_id(
    organization_id: Annotated[
        UUID | None,
        Query(description="Optional target tenant organization ID"),
    ] = None,
    x_organization_id: Annotated[
        UUID | None,
        Header(
            alias="X-Organization-ID", description="Optional target tenant organization ID header"
        ),
    ] = None,
) -> UUID | None:
    """Resolve target organization ID optionally from query parameter or request header."""
    return organization_id or x_organization_id


async def get_tenant_context_from_request(
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    organization_id: Annotated[UUID, Depends(get_requested_organization_id)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> TenantContext:
    """Resolve active TenantContext from query parameter or header."""
    resolver = TenantResolver(session)
    try:
        return await resolver.resolve(
            principal=principal,
            organization_id=organization_id,
            correlation_id=x_request_id,
        )
    except TenantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except TenantSuspendedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except (TenantAccessDeniedError, RestaurantAccessDeniedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


__all__ = [
    "TenantContext",
    "get_optional_organization_id",
    "get_requested_organization_id",
    "get_restaurant_tenant_context",
    "get_tenant_context",
    "get_tenant_context_from_request",
]
