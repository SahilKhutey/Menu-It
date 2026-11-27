"""Modular restaurant domain API router (FCD-07 §7.2, FCD-14 §7.2)."""

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
    RestaurantMemberAssignRequest,
    RestaurantMemberResponse,
    RestaurantSettingsResponse,
    RestaurantSettingsUpdateRequest,
    RestaurantSummaryResponse,
    UpdateRestaurantRequest,
)
from menu_it.authorization.permissions import Permission
from menu_it.authorization.policies import ORGANIZATION_ROLE_PERMISSIONS
from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.database.models.restaurant_membership import RestaurantRole
from menu_it.database.session import get_db_session
from menu_it.domain.base.errors import DomainError, EntityNotFoundError
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.infrastructure.idempotency.dependency import (
    IdempotencyContext,
    check_idempotency,
)
from menu_it.repositories.tenant_restaurants import TenantRestaurantRepository
from menu_it.schemas.branches import BranchCreateRequest, BranchResponse
from menu_it.services.branch_management import BranchManagementService
from menu_it.services.restaurant_lifecycle import InvalidRestaurantTransition
from menu_it.services.restaurant_management import RestaurantManagementService

router = APIRouter()


def _check_perm(tenant: TenantContext, permission: Permission) -> None:
    perms = ORGANIZATION_ROLE_PERMISSIONS.get(tenant.organization_role, set())
    if permission not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission.value}' required.",
        )


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, EntityNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, ResourceConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if isinstance(exc, (DomainError, InvalidRestaurantTransition)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    raise exc


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

    count_stmt = (
        select(func.count())
        .select_from(Restaurant)
        .where(Restaurant.organization_id == tenant.organization_id)
    )
    count_result = await session.execute(count_stmt)
    total_items = count_result.scalar_one()

    summaries = [RestaurantSummaryResponse.model_validate(r) for r in items]

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

    return success_response(
        data=RestaurantSummaryResponse.model_validate(restaurant),
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
    _check_perm(tenant, Permission.RESTAURANT_CREATE)
    svc = RestaurantManagementService(session)
    try:
        created = await svc.create_restaurant(
            organization_id=tenant.organization_id,
            actor_user_id=tenant.user_id,
            name=payload.name,
            slug=payload.slug,
            timezone=payload.timezone,
            description=payload.description,
            email=payload.email,
            phone=payload.phone,
            website=payload.website,
            cuisine_type=payload.cuisine_type,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(created)
    except Exception as exc:
        await session.rollback()
        _handle_error(exc)
        raise

    summary = RestaurantSummaryResponse.model_validate(created)
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


@router.patch(
    "/{restaurant_id}",
    response_model=APIResponse[RestaurantSummaryResponse],
    summary="Update restaurant details",
)
async def update_restaurant(
    restaurant_id: UUID,
    payload: UpdateRestaurantRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[RestaurantSummaryResponse]:
    """Update restaurant profile fields."""
    _check_perm(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantManagementService(session)
    try:
        updated = await svc.update_restaurant(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            name=payload.name,
            timezone=payload.timezone,
            description=payload.description,
            email=payload.email,
            phone=payload.phone,
            website=payload.website,
            cuisine_type=payload.cuisine_type,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(updated)
    except Exception as exc:
        await session.rollback()
        _handle_error(exc)
        raise

    return success_response(
        data=RestaurantSummaryResponse.model_validate(updated),
        request_id=get_request_id(request),
    )


@router.post(
    "/{restaurant_id}/activate",
    response_model=APIResponse[RestaurantSummaryResponse],
    summary="Activate restaurant",
)
async def activate_restaurant(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[RestaurantSummaryResponse]:
    """Activate a suspended or inactive restaurant."""
    _check_perm(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantManagementService(session)
    try:
        updated = await svc.transition_status(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            target_status=RestaurantStatus.ACTIVE,
            actor_user_id=tenant.user_id,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(updated)
    except Exception as exc:
        await session.rollback()
        _handle_error(exc)
        raise

    return success_response(
        data=RestaurantSummaryResponse.model_validate(updated),
        request_id=get_request_id(request),
    )


@router.post(
    "/{restaurant_id}/suspend",
    response_model=APIResponse[RestaurantSummaryResponse],
    summary="Suspend restaurant",
)
async def suspend_restaurant(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[RestaurantSummaryResponse]:
    """Suspend an active restaurant."""
    _check_perm(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantManagementService(session)
    try:
        updated = await svc.transition_status(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            target_status=RestaurantStatus.SUSPENDED,
            actor_user_id=tenant.user_id,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(updated)
    except Exception as exc:
        await session.rollback()
        _handle_error(exc)
        raise

    return success_response(
        data=RestaurantSummaryResponse.model_validate(updated),
        request_id=get_request_id(request),
    )


@router.get(
    "/{restaurant_id}/settings",
    response_model=APIResponse[RestaurantSettingsResponse],
    summary="Get restaurant settings",
)
async def get_restaurant_settings(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[RestaurantSettingsResponse]:
    """Retrieve restaurant-specific operational settings."""
    _check_perm(tenant, Permission.RESTAURANT_READ)
    svc = RestaurantManagementService(session)
    try:
        rec = await svc.get_settings(
            organization_id=tenant.organization_id, restaurant_id=restaurant_id
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
        raise

    return success_response(
        data=RestaurantSettingsResponse.model_validate(rec),
        request_id=get_request_id(request),
    )


@router.patch(
    "/{restaurant_id}/settings",
    response_model=APIResponse[RestaurantSettingsResponse],
    summary="Update restaurant settings",
)
async def update_restaurant_settings(
    restaurant_id: UUID,
    payload: RestaurantSettingsUpdateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[RestaurantSettingsResponse]:
    """Update restaurant-specific operational settings."""
    _check_perm(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantManagementService(session)
    try:
        rec = await svc.update_settings(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            settings_payload=payload.settings_payload,
        )
        await session.commit()
        await session.refresh(rec)
    except Exception as exc:
        await session.rollback()
        _handle_error(exc)
        raise

    return success_response(
        data=RestaurantSettingsResponse.model_validate(rec),
        request_id=get_request_id(request),
    )


@router.get(
    "/{restaurant_id}/members",
    response_model=APIResponse[list[RestaurantMemberResponse]],
    summary="List restaurant members",
)
async def list_restaurant_members(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[list[RestaurantMemberResponse]]:
    """List restaurant-scoped role assignments."""
    _check_perm(tenant, Permission.RESTAURANT_READ)
    svc = RestaurantManagementService(session)
    try:
        items = await svc.list_members(
            organization_id=tenant.organization_id, restaurant_id=restaurant_id
        )
    except Exception as exc:
        _handle_error(exc)
        raise

    return success_response(
        data=[RestaurantMemberResponse.model_validate(m) for m in items],
        request_id=get_request_id(request),
    )


@router.put(
    "/{restaurant_id}/members/{user_id}",
    response_model=APIResponse[RestaurantMemberResponse],
    summary="Assign or update restaurant member role",
)
async def assign_restaurant_member(
    restaurant_id: UUID,
    user_id: UUID,
    payload: RestaurantMemberAssignRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[RestaurantMemberResponse]:
    """Assign an organization member to a restaurant-specific role."""
    _check_perm(tenant, Permission.STAFF_UPDATE)
    svc = RestaurantManagementService(session)
    try:
        role_enum = RestaurantRole(payload.role)
        membership = await svc.assign_member(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            user_id=user_id,
            role=role_enum,
        )
        await session.commit()
        await session.refresh(membership)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except Exception as exc:
        await session.rollback()
        _handle_error(exc)
        raise

    return success_response(
        data=RestaurantMemberResponse.model_validate(membership),
        request_id=get_request_id(request),
    )


@router.post(
    "/{restaurant_id}/branches",
    response_model=APIResponse[BranchResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create physical branch under restaurant",
)
async def create_restaurant_branch(
    restaurant_id: UUID,
    payload: BranchCreateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[BranchResponse]:
    """Create a physical branch under the specified active restaurant."""
    _check_perm(tenant, Permission.BRANCH_CREATE)
    svc = BranchManagementService(session)
    try:
        branch = await svc.create_branch(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            name=payload.name,
            slug=payload.slug,
            timezone=payload.timezone,
            country_code=payload.country_code,
            branch_code=payload.branch_code,
            email=payload.email,
            phone=payload.phone,
            address_line_1=payload.address_line_1,
            address_line_2=payload.address_line_2,
            city=payload.city,
            state_region=payload.state_region,
            postal_code=payload.postal_code,
            latitude=payload.latitude,
            longitude=payload.longitude,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(branch)
    except Exception as exc:
        await session.rollback()
        _handle_error(exc)
        raise

    return success_response(
        data=BranchResponse.model_validate(branch),
        request_id=get_request_id(request),
    )


@router.get(
    "/{restaurant_id}/branches",
    response_model=APIResponse[list[BranchResponse]],
    summary="List branches under restaurant",
)
async def list_restaurant_branches(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[list[BranchResponse]]:
    """List all physical branches belonging to the restaurant."""
    _check_perm(tenant, Permission.BRANCH_READ)
    svc = BranchManagementService(session)
    try:
        items = await svc.list_branches(
            organization_id=tenant.organization_id, restaurant_id=restaurant_id
        )
    except Exception as exc:
        _handle_error(exc)
        raise

    return success_response(
        data=[BranchResponse.model_validate(b) for b in items],
        request_id=get_request_id(request),
    )
