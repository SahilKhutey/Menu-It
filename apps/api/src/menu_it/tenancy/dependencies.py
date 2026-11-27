"""FastAPI dependencies for tenant context resolution (FCD-04 §10.1)."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.auth.dependencies import get_current_principal
from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.database.session import get_db_session
from menu_it.tenancy.context import TenantContext
from menu_it.tenancy.exceptions import (
    RestaurantAccessDeniedError,
    TenantAccessDeniedError,
    TenantNotFoundError,
    TenantSuspendedError,
)
from menu_it.tenancy.resolver import TenantResolver


async def get_tenant_context(
    organization_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(get_current_principal),
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    x_request_id: Annotated[
        str | None,
        Header(alias="X-Request-ID"),
    ] = None,
) -> TenantContext:
    """FastAPI dependency resolving organization-level TenantContext."""
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


async def get_restaurant_tenant_context(
    organization_id: UUID,
    restaurant_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(get_current_principal),
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    x_request_id: Annotated[
        str | None,
        Header(alias="X-Request-ID"),
    ] = None,
) -> TenantContext:
    """FastAPI dependency resolving restaurant-scoped TenantContext."""
    resolver = TenantResolver(session)
    try:
        return await resolver.resolve(
            principal=principal,
            organization_id=organization_id,
            restaurant_id=restaurant_id,
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
