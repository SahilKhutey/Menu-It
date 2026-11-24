"""Modular restaurant domain API router (FCD-07 §7.2)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.api.dependencies.pagination import get_pagination_params
from menu_it.api.dependencies.request_context import get_request_id
from menu_it.api.dependencies.tenant import (
    TenantContext,
    get_tenant_context_from_request,
)
from menu_it.api.exceptions.responses import success_response
from menu_it.api.schemas.common import APIResponse
from menu_it.api.schemas.pagination import (
    PaginatedData,
    PaginationMeta,
    PaginationParams,
)
from menu_it.api.v1.modules.restaurants.schemas import (
    CreateRestaurantRequest,
    RestaurantSummaryResponse,
)
from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.database.session import get_db_session
from menu_it.infrastructure.idempotency.dependency import (
    IdempotencyContext,
    check_idempotency,
)
from menu_it.repositories.tenant_restaurants import TenantRestaurantRepository

router = APIRouter()


@router.get(
    "",
    response_model=APIResponse[PaginatedData[RestaurantSummaryResponse]],
    status_code=status.HTTP_200_OK,
    summary="List accessible restaurants",
)
async def list_restaurants(
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
) -> APIResponse[PaginatedData[RestaurantSummaryResponse]]:
    """List restaurants owned by the active organization with pagination."""
    repo = TenantRestaurantRepository(session, tenant)
    items = await repo.list_restaurants(
        offset=pagination.offset,
        limit=pagination.page_size,
    )

    # Count total items within tenant boundary
    count_stmt = (
        select(func.count())
        .select_from(Restaurant)
        .where(Restaurant.organization_id == tenant.organization_id)
    )
    count_result = await session.execute(count_stmt)
    total_items = count_result.scalar_one()

    summaries = [
        RestaurantSummaryResponse(
            id=r.id,
            organization_id=r.organization_id,
            name=r.name,
            slug=r.slug,
            timezone=r.timezone,
            status=r.status.value,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in items
    ]

    meta = PaginationMeta.build(
        page=pagination.page,
        page_size=pagination.page_size,
        total_items=total_items,
    )

    return success_response(
        data=PaginatedData(items=summaries, pagination=meta),
        request_id=get_request_id(request),
    )


@router.get(
    "/{restaurant_id}",
    response_model=APIResponse[RestaurantSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get restaurant details",
)
async def get_restaurant(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[RestaurantSummaryResponse]:
    """Retrieve details for a specific restaurant scoped to active organization."""
    repo = TenantRestaurantRepository(session, tenant)
    restaurant = await repo.get_by_id(restaurant_id)
    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant '{restaurant_id}' not found.",
        )

    summary = RestaurantSummaryResponse(
        id=restaurant.id,
        organization_id=restaurant.organization_id,
        name=restaurant.name,
        slug=restaurant.slug,
        timezone=restaurant.timezone,
        status=restaurant.status.value,
        created_at=restaurant.created_at,
        updated_at=restaurant.updated_at,
    )
    return success_response(
        data=summary,
        request_id=get_request_id(request),
    )


@router.post(
    "",
    response_model=APIResponse[RestaurantSummaryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create restaurant location",
)
async def create_restaurant(
    payload: CreateRestaurantRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    idempotency: Annotated[IdempotencyContext | None, Depends(check_idempotency)] = None,
) -> APIResponse[RestaurantSummaryResponse]:
    """Create a new restaurant location strictly scoped to the active tenant."""
    repo = TenantRestaurantRepository(session, tenant)

    # Check for duplicate slug within organization
    existing = await repo.get_by_slug(payload.slug)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Restaurant with slug '{payload.slug}' already exists in this organization.",
        )

    restaurant = Restaurant(
        organization_id=tenant.organization_id,
        name=payload.name,
        slug=payload.slug,
        timezone=payload.timezone,
        status=RestaurantStatus.ACTIVE,
    )
    created = await repo.create(restaurant)
    await session.commit()

    summary = RestaurantSummaryResponse(
        id=created.id,
        organization_id=created.organization_id,
        name=created.name,
        slug=created.slug,
        timezone=created.timezone,
        status=created.status.value,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )
    response_data = success_response(
        data=summary,
        request_id=get_request_id(request),
    )

    if idempotency is not None:
        await idempotency.save(
            session=session,
            response_status=status.HTTP_201_CREATED,
            response_body=response_data.model_dump(mode="json"),
        )

    return response_data
