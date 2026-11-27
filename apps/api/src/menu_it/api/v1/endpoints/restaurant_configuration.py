"""FCD-15 Restaurant Profile, Branding, Schedule, Service, and Publication API endpoints."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.api.dependencies.request_context import get_request_id
from menu_it.api.dependencies.tenant import TenantContext, get_tenant_context_from_request
from menu_it.api.exceptions.responses import success_response
from menu_it.api.schemas.common import APIResponse
from menu_it.authorization.permissions import Permission
from menu_it.authorization.policies import ORGANIZATION_ROLE_PERMISSIONS
from menu_it.database.session import get_db_session
from menu_it.domain.base.errors import (
    ConcurrencyConflictError,
    DomainError,
    EntityNotFoundError,
)
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.schemas.restaurant_configuration import (
    BranchConfigurationResetRequest,
    BranchConfigurationUpdateRequest,
    ConfigurationRevisionResponse,
    EffectiveConfigurationResponse,
    OperationalSettingsResponse,
    OperationalSettingsUpdateRequest,
    PublishProfileRequest,
    RestaurantBrandingResponse,
    RestaurantBrandingUpdateRequest,
    RestaurantProfileConfigResponse,
    RestaurantProfileConfigUpdateRequest,
    RestaurantPublicationResponse,
    ScheduleExceptionResponse,
    ScheduleExceptionUpsertRequest,
    ServiceModeResponse,
    ServiceModesUpdateRequest,
    WeeklyHourRowResponse,
    WeeklyHoursReplaceRequest,
)
from menu_it.services.restaurant_configuration import RestaurantConfigurationService
from menu_it.services.restaurant_publication import RestaurantPublicationService

router = APIRouter()


def _require_permission(tenant: TenantContext, permission: Permission) -> None:
    perms = ORGANIZATION_ROLE_PERMISSIONS.get(tenant.organization_role, set())
    if permission not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission.value}' required.",
        )


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, EntityNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, (ConcurrencyConflictError, ResourceConflictError)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if isinstance(exc, DomainError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    raise exc


# ------------------------------------------------------------------
# Profile
# ------------------------------------------------------------------
@router.get(
    "/restaurants/{restaurant_id}/profile",
    response_model=APIResponse[RestaurantProfileConfigResponse],
    tags=["Restaurant Configuration"],
)
async def get_restaurant_profile(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_READ)
    svc = RestaurantConfigurationService(session)
    try:
        record = await svc.get_profile(tenant.organization_id, restaurant_id)
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=RestaurantProfileConfigResponse(
            id=record.id,
            organization_id=record.organization_id,
            restaurant_id=record.restaurant_id,
            display_name=record.public_name,
            short_description=record.short_description,
            description=record.description,
            cuisine_type=record.cuisine_type,
            price_range=record.price_range,
            website_url=record.website_url,
            public_email=record.public_email,
            public_phone=record.public_phone,
            social_links=dict(record.social_links or {}),
            version=record.version,
        ),
        request_id=get_request_id(request),
    )


@router.patch(
    "/restaurants/{restaurant_id}/profile",
    response_model=APIResponse[RestaurantProfileConfigResponse],
    tags=["Restaurant Configuration"],
)
async def update_restaurant_profile(
    restaurant_id: UUID,
    payload: RestaurantProfileConfigUpdateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        record = await svc.update_profile(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            correlation_id=get_request_id(request),
            **payload.model_dump(),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=RestaurantProfileConfigResponse(
            id=record.id,
            organization_id=record.organization_id,
            restaurant_id=record.restaurant_id,
            display_name=record.public_name,
            short_description=record.short_description,
            description=record.description,
            cuisine_type=record.cuisine_type,
            price_range=record.price_range,
            website_url=record.website_url,
            public_email=record.public_email,
            public_phone=record.public_phone,
            social_links=dict(record.social_links or {}),
            version=record.version,
        ),
        request_id=get_request_id(request),
    )


# ------------------------------------------------------------------
# Branding
# ------------------------------------------------------------------
@router.get(
    "/restaurants/{restaurant_id}/branding",
    response_model=APIResponse[RestaurantBrandingResponse],
    tags=["Restaurant Configuration"],
)
async def get_restaurant_branding(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_READ)
    svc = RestaurantConfigurationService(session)
    try:
        branding = await svc.get_branding(tenant.organization_id, restaurant_id)
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=RestaurantBrandingResponse.model_validate(branding, from_attributes=True),
        request_id=get_request_id(request),
    )


@router.put(
    "/restaurants/{restaurant_id}/branding",
    response_model=APIResponse[RestaurantBrandingResponse],
    tags=["Restaurant Configuration"],
)
async def update_restaurant_branding(
    restaurant_id: UUID,
    payload: RestaurantBrandingUpdateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        branding = await svc.update_branding(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            correlation_id=get_request_id(request),
            **payload.model_dump(),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=RestaurantBrandingResponse.model_validate(branding, from_attributes=True),
        request_id=get_request_id(request),
    )


# ------------------------------------------------------------------
# Weekly Hours & Schedule Exceptions
# ------------------------------------------------------------------
@router.get(
    "/restaurants/{restaurant_id}/hours",
    response_model=APIResponse[list[WeeklyHourRowResponse]],
    tags=["Restaurant Configuration"],
)
async def get_restaurant_hours(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_READ)
    svc = RestaurantConfigurationService(session)
    try:
        rows = await svc.get_weekly_hours(tenant.organization_id, restaurant_id)
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=[WeeklyHourRowResponse.model_validate(r, from_attributes=True) for r in rows],
        request_id=get_request_id(request),
    )


@router.put(
    "/restaurants/{restaurant_id}/hours",
    response_model=APIResponse[list[WeeklyHourRowResponse]],
    tags=["Restaurant Configuration"],
)
async def replace_restaurant_hours(
    restaurant_id: UUID,
    payload: WeeklyHoursReplaceRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        rows = await svc.replace_weekly_hours(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            days=[d.model_dump() for d in payload.days],
            correlation_id=get_request_id(request),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=[WeeklyHourRowResponse.model_validate(r, from_attributes=True) for r in rows],
        request_id=get_request_id(request),
    )


@router.get(
    "/restaurants/{restaurant_id}/schedule-exceptions",
    response_model=APIResponse[list[ScheduleExceptionResponse]],
    tags=["Restaurant Configuration"],
)
async def list_restaurant_schedule_exceptions(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_READ)
    svc = RestaurantConfigurationService(session)
    try:
        rows = await svc.list_schedule_exceptions(tenant.organization_id, restaurant_id)
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=[ScheduleExceptionResponse.model_validate(r, from_attributes=True) for r in rows],
        request_id=get_request_id(request),
    )


@router.post(
    "/restaurants/{restaurant_id}/schedule-exceptions",
    response_model=APIResponse[ScheduleExceptionResponse],
    status_code=status.HTTP_201_CREATED,
    tags=["Restaurant Configuration"],
)
async def upsert_restaurant_schedule_exception(
    restaurant_id: UUID,
    payload: ScheduleExceptionUpsertRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        record = await svc.upsert_schedule_exception(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            exception_date=payload.exception_date,
            exception_type=payload.exception_type,
            reason=payload.reason,
            intervals=[iv.model_dump() for iv in payload.intervals],
            correlation_id=get_request_id(request),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=ScheduleExceptionResponse.model_validate(record, from_attributes=True),
        request_id=get_request_id(request),
    )


@router.delete(
    "/restaurants/{restaurant_id}/schedule-exceptions/{exception_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Restaurant Configuration"],
)
async def delete_restaurant_schedule_exception(
    restaurant_id: UUID,
    exception_id: UUID,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    _require_permission(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        await svc.delete_schedule_exception(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            exception_id=exception_id,
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)


# ------------------------------------------------------------------
# Services & Operational Settings
# ------------------------------------------------------------------
@router.get(
    "/restaurants/{restaurant_id}/services",
    response_model=APIResponse[list[ServiceModeResponse]],
    tags=["Restaurant Configuration"],
)
async def get_restaurant_services(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_READ)
    svc = RestaurantConfigurationService(session)
    try:
        rows = await svc.get_service_modes(tenant.organization_id, restaurant_id)
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=[ServiceModeResponse.model_validate(r, from_attributes=True) for r in rows],
        request_id=get_request_id(request),
    )


@router.put(
    "/restaurants/{restaurant_id}/services",
    response_model=APIResponse[list[ServiceModeResponse]],
    tags=["Restaurant Configuration"],
)
async def update_restaurant_services(
    restaurant_id: UUID,
    payload: ServiceModesUpdateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        rows = await svc.update_service_modes(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            modes=[m.model_dump() for m in payload.modes],
            correlation_id=get_request_id(request),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=[ServiceModeResponse.model_validate(r, from_attributes=True) for r in rows],
        request_id=get_request_id(request),
    )


@router.get(
    "/restaurants/{restaurant_id}/operations",
    response_model=APIResponse[OperationalSettingsResponse],
    tags=["Restaurant Configuration"],
)
async def get_restaurant_operations(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_READ)
    svc = RestaurantConfigurationService(session)
    try:
        ops = await svc.get_operational_settings(tenant.organization_id, restaurant_id)
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=OperationalSettingsResponse.model_validate(ops, from_attributes=True),
        request_id=get_request_id(request),
    )


@router.put(
    "/restaurants/{restaurant_id}/operations",
    response_model=APIResponse[OperationalSettingsResponse],
    tags=["Restaurant Configuration"],
)
async def update_restaurant_operations(
    restaurant_id: UUID,
    payload: OperationalSettingsUpdateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        ops = await svc.update_operational_settings(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            correlation_id=get_request_id(request),
            **payload.model_dump(),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=OperationalSettingsResponse.model_validate(ops, from_attributes=True),
        request_id=get_request_id(request),
    )


# ------------------------------------------------------------------
# Branch Configuration & Effective Resolution
# ------------------------------------------------------------------
@router.get(
    "/branches/{branch_id}/configuration",
    response_model=APIResponse[EffectiveConfigurationResponse],
    tags=["Branch Configuration"],
)
async def get_effective_branch_configuration(
    branch_id: UUID,
    restaurant_id: Annotated[UUID, Query()],
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.BRANCH_READ)
    svc = RestaurantConfigurationService(session)
    try:
        effective = await svc.resolve_effective_configuration(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            branch_id=branch_id,
        )
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=EffectiveConfigurationResponse(
            organization_id=effective.organization_id,
            restaurant_id=effective.restaurant_id,
            branch_id=effective.branch_id,
            display_name=effective.display_name,
            timezone=effective.timezone,
            currency_code=effective.currency_code,
            public_phone=effective.public_phone,
            enabled_services=list(effective.enabled_services),
            operational_settings={
                "preparation_buffer_minutes": (
                    effective.operational_settings.preparation_buffer_minutes
                ),
                "minimum_notice_minutes": effective.operational_settings.minimum_notice_minutes,
                "maximum_advance_days": effective.operational_settings.maximum_advance_days,
                "max_concurrent_orders": effective.operational_settings.max_concurrent_orders,
                "auto_accept_orders": effective.operational_settings.auto_accept_orders,
            },
            revision=effective.revision,
        ),
        request_id=get_request_id(request),
    )


@router.patch(
    "/branches/{branch_id}/configuration",
    response_model=APIResponse[dict[str, Any]],
    tags=["Branch Configuration"],
)
async def update_branch_configuration(
    branch_id: UUID,
    restaurant_id: Annotated[UUID, Query()],
    payload: BranchConfigurationUpdateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.BRANCH_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        cfg = await svc.update_branch_configuration(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            branch_id=branch_id,
            actor_user_id=tenant.user_id,
            correlation_id=get_request_id(request),
            **payload.model_dump(),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data={
            "id": str(cfg.id),
            "branch_id": str(cfg.branch_id),
            "schedule_override_enabled": cfg.schedule_override_enabled,
            "service_override_enabled": cfg.service_override_enabled,
            "revision": cfg.revision,
        },
        request_id=get_request_id(request),
    )


@router.put(
    "/branches/{branch_id}/services",
    response_model=APIResponse[list[ServiceModeResponse]],
    tags=["Branch Configuration"],
)
async def update_branch_services(
    branch_id: UUID,
    restaurant_id: Annotated[UUID, Query()],
    payload: ServiceModesUpdateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.BRANCH_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        rows = await svc.update_branch_service_modes(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            branch_id=branch_id,
            actor_user_id=tenant.user_id,
            modes=[m.model_dump() for m in payload.modes],
            correlation_id=get_request_id(request),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=[ServiceModeResponse.model_validate(r, from_attributes=True) for r in rows],
        request_id=get_request_id(request),
    )


@router.put(
    "/branches/{branch_id}/hours",
    response_model=APIResponse[list[WeeklyHourRowResponse]],
    tags=["Branch Configuration"],
)
async def replace_branch_hours(
    branch_id: UUID,
    restaurant_id: Annotated[UUID, Query()],
    payload: WeeklyHoursReplaceRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.BRANCH_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        rows = await svc.replace_branch_weekly_hours(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            branch_id=branch_id,
            actor_user_id=tenant.user_id,
            days=[d.model_dump() for d in payload.days],
            correlation_id=get_request_id(request),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=[WeeklyHourRowResponse.model_validate(r, from_attributes=True) for r in rows],
        request_id=get_request_id(request),
    )


@router.post(
    "/branches/{branch_id}/configuration/reset",
    response_model=APIResponse[dict[str, Any]],
    tags=["Branch Configuration"],
)
async def reset_branch_configuration(
    branch_id: UUID,
    restaurant_id: Annotated[UUID, Query()],
    payload: BranchConfigurationResetRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.BRANCH_UPDATE)
    svc = RestaurantConfigurationService(session)
    try:
        cfg = await svc.reset_branch_configuration(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            branch_id=branch_id,
            actor_user_id=tenant.user_id,
            reset_schedule=payload.reset_schedule,
            reset_services=payload.reset_services,
            correlation_id=get_request_id(request),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data={"branch_id": str(cfg.branch_id), "revision": cfg.revision, "reset": True},
        request_id=get_request_id(request),
    )


# ------------------------------------------------------------------
# Public Profile & Publications
# ------------------------------------------------------------------
@router.post(
    "/restaurants/{restaurant_id}/publish",
    response_model=APIResponse[RestaurantPublicationResponse],
    tags=["Restaurant Publications"],
)
async def publish_restaurant_profile(
    restaurant_id: UUID,
    payload: PublishProfileRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantPublicationService(session)
    try:
        pub = await svc.publish(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            public_slug=payload.public_slug,
            change_summary=payload.change_summary,
            correlation_id=get_request_id(request),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=RestaurantPublicationResponse.model_validate(pub, from_attributes=True),
        request_id=get_request_id(request),
    )


@router.post(
    "/restaurants/{restaurant_id}/unpublish",
    response_model=APIResponse[RestaurantPublicationResponse],
    tags=["Restaurant Publications"],
)
async def unpublish_restaurant_profile(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantPublicationService(session)
    try:
        pub = await svc.unpublish(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=tenant.user_id,
            correlation_id=get_request_id(request),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=RestaurantPublicationResponse.model_validate(pub, from_attributes=True),
        request_id=get_request_id(request),
    )


@router.get(
    "/restaurants/{restaurant_id}/publications",
    response_model=APIResponse[list[ConfigurationRevisionResponse]],
    tags=["Restaurant Publications"],
)
async def list_restaurant_publications(
    restaurant_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_READ)
    svc = RestaurantPublicationService(session)
    try:
        revs = await svc.list_publications(tenant.organization_id, restaurant_id)
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=[ConfigurationRevisionResponse.model_validate(r, from_attributes=True) for r in revs],
        request_id=get_request_id(request),
    )


@router.post(
    "/restaurants/{restaurant_id}/publications/{revision_number}/restore",
    response_model=APIResponse[RestaurantPublicationResponse],
    tags=["Restaurant Publications"],
)
async def restore_restaurant_publication(
    restaurant_id: UUID,
    revision_number: int,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    _require_permission(tenant, Permission.RESTAURANT_UPDATE)
    svc = RestaurantPublicationService(session)
    try:
        pub = await svc.restore_revision(
            organization_id=tenant.organization_id,
            restaurant_id=restaurant_id,
            revision_number=revision_number,
            actor_user_id=tenant.user_id,
            correlation_id=get_request_id(request),
        )
        await session.commit()
    except Exception as exc:
        _handle_error(exc)
    return success_response(
        data=RestaurantPublicationResponse.model_validate(pub, from_attributes=True),
        request_id=get_request_id(request),
    )


@router.get(
    "/public/restaurants/{slug}",
    response_model=APIResponse[dict[str, Any]],
    tags=["Public Restaurant Profiles"],
)
async def get_public_restaurant_profile(
    slug: str,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    svc = RestaurantPublicationService(session)
    try:
        snapshot = await svc.get_public_profile_by_slug(slug)
    except Exception as exc:
        _handle_error(exc)
    return success_response(data=snapshot, request_id=get_request_id(request))
