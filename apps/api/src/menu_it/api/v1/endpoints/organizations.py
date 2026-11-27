"""Organization, Membership, Invitation & Org-Scoped Restaurant endpoints (FCD-14 §7.1)."""

import contextlib
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.api.dependencies.pagination import get_pagination_params
from menu_it.api.dependencies.request_context import get_request_id
from menu_it.api.exceptions.responses import success_response
from menu_it.api.schemas.common import APIResponse as EnvelopeResponse
from menu_it.api.schemas.pagination import PaginatedData, PaginationMeta, PaginationParams
from menu_it.api.v1.modules.restaurants.schemas import (
    CreateRestaurantRequest,
    RestaurantSummaryResponse,
)
from menu_it.auth.dependencies import get_current_principal
from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.authorization.dependencies import require_permission
from menu_it.authorization.permissions import Permission
from menu_it.authorization.policies import ORGANIZATION_ROLE_PERMISSIONS
from menu_it.database.models.organization_membership import MembershipStatus, OrganizationRole
from menu_it.database.models.user import User
from menu_it.database.session import get_db_session
from menu_it.domain.base.errors import DomainError, EntityNotFoundError
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.schemas.common import APIResponse, ResponseMetadata
from menu_it.schemas.organizations import (
    InvitationAcceptRequest,
    InvitationCreateRequest,
    InvitationResponse,
    OrganizationCreateRequest,
    OrganizationMemberResponse,
    OrganizationMemberUpdateRequest,
    OrganizationResponse,
    OrganizationSettingsResponse,
    OrganizationSettingsUpdateRequest,
    OrganizationUpdateRequest,
    OwnershipTransferRequest,
)
from menu_it.services.membership_and_invitation import MembershipAndInvitationService
from menu_it.services.organization_lifecycle import InvalidOrganizationTransition
from menu_it.services.organization_management import OrganizationManagementService
from menu_it.services.restaurant_management import RestaurantManagementService
from menu_it.tenancy.context import TenantContext
from menu_it.tenancy.dependencies import get_tenant_context

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


def _handle_domain_error(exc: Exception) -> None:
    if isinstance(exc, EntityNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, ResourceConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if isinstance(exc, (DomainError, InvalidOrganizationTransition)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    raise exc


@router.post(
    "",
    response_model=EnvelopeResponse[OrganizationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create and onboard a new organization",
)
async def create_organization(
    payload: OrganizationCreateRequest,
    request: Request,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[OrganizationResponse]:
    """Onboard a new organization and atomically assign the caller as initial owner."""
    svc = OrganizationManagementService(session)
    req_id = str(get_request_id(request))
    try:
        org, _ = await svc.create_organization(
            name=payload.name,
            slug=payload.slug,
            actor_user_id=principal.user_id,
            currency_code=payload.currency_code,
            timezone=payload.timezone,
            country_code=payload.country_code,
            legal_name=payload.legal_name,
            organization_type=payload.organization_type,
            email=payload.email,
            phone=payload.phone,
            website=payload.website,
            correlation_id=req_id,
        )
        await session.commit()
        await session.refresh(org)
    except Exception as exc:
        await session.rollback()
        _handle_domain_error(exc)
        raise

    return success_response(
        data=OrganizationResponse.model_validate(org),
        request_id=get_request_id(request),
    )


@router.get(
    "",
    response_model=EnvelopeResponse[list[OrganizationResponse]],
    summary="List organizations accessible to current user",
)
async def list_organizations(
    request: Request,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[list[OrganizationResponse]]:
    """List all active organizations the authenticated user belongs to."""
    svc = OrganizationManagementService(session)
    orgs = await svc.list_user_organizations(principal.user_id)
    return success_response(
        data=[OrganizationResponse.model_validate(o) for o in orgs],
        request_id=get_request_id(request),
    )


@router.post(
    "/invitations/accept",
    response_model=EnvelopeResponse[OrganizationMemberResponse],
    summary="Accept an organization invitation token",
)
async def accept_invitation(
    payload: InvitationAcceptRequest,
    request: Request,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[OrganizationMemberResponse]:
    """Accept a pending invitation token for the authenticated user's email."""
    user = (
        await session.execute(select(User).where(User.id == principal.user_id))
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    svc = MembershipAndInvitationService(session)
    try:
        membership = await svc.accept_invitation(
            raw_token=payload.token,
            actor_user_id=principal.user_id,
            actor_email=user.email,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(membership)
    except Exception as exc:
        await session.rollback()
        _handle_domain_error(exc)
        raise

    return success_response(
        data=OrganizationMemberResponse.model_validate(membership),
        request_id=get_request_id(request),
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
        },
        meta=ResponseMetadata(request_id=req_id),
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


@router.get(
    "/{organization_id}",
    response_model=EnvelopeResponse[OrganizationResponse],
    summary="Get organization profile",
)
async def get_organization(
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_permission(Permission.ORGANIZATION_READ))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[OrganizationResponse]:
    """Retrieve organization details scoped to active membership."""
    svc = OrganizationManagementService(session)
    org = await svc.get_organization(tenant.organization_id)
    return success_response(
        data=OrganizationResponse.model_validate(org),
        request_id=get_request_id(request),
    )


@router.patch(
    "/{organization_id}",
    response_model=EnvelopeResponse[OrganizationResponse],
    summary="Update organization profile",
)
async def update_organization(
    payload: OrganizationUpdateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_permission(Permission.ORGANIZATION_UPDATE))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[OrganizationResponse]:
    """Update organization profile fields."""
    svc = OrganizationManagementService(session)
    try:
        org = await svc.update_organization(
            organization_id=tenant.organization_id,
            actor_user_id=tenant.user_id,
            name=payload.name,
            legal_name=payload.legal_name,
            email=payload.email,
            phone=payload.phone,
            website=payload.website,
            country_code=payload.country_code,
            currency_code=payload.currency_code,
            timezone=payload.timezone,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(org)
    except Exception as exc:
        await session.rollback()
        _handle_domain_error(exc)
        raise

    return success_response(
        data=OrganizationResponse.model_validate(org),
        request_id=get_request_id(request),
    )


@router.post(
    "/{organization_id}/suspend",
    response_model=EnvelopeResponse[OrganizationResponse],
    summary="Suspend organization",
)
async def suspend_organization(
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_permission(Permission.ORGANIZATION_SUSPEND))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[OrganizationResponse]:
    """Suspend an organization via FCD-04 lifecycle rules."""
    svc = OrganizationManagementService(session)
    try:
        org = await svc.suspend_organization(
            organization_id=tenant.organization_id,
            actor_user_id=tenant.user_id,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(org)
    except Exception as exc:
        await session.rollback()
        _handle_domain_error(exc)
        raise

    return success_response(
        data=OrganizationResponse.model_validate(org),
        request_id=get_request_id(request),
    )


@router.get(
    "/{organization_id}/settings",
    response_model=EnvelopeResponse[OrganizationSettingsResponse],
    summary="Get organization settings",
)
async def get_organization_settings(
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_permission(Permission.ORGANIZATION_READ))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[OrganizationSettingsResponse]:
    """Retrieve organization-level configuration settings."""
    svc = OrganizationManagementService(session)
    settings_rec = await svc.get_settings(tenant.organization_id)
    await session.commit()
    return success_response(
        data=OrganizationSettingsResponse.model_validate(settings_rec),
        request_id=get_request_id(request),
    )


@router.patch(
    "/{organization_id}/settings",
    response_model=EnvelopeResponse[OrganizationSettingsResponse],
    summary="Update organization settings",
)
async def update_organization_settings(
    payload: OrganizationSettingsUpdateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_permission(Permission.ORGANIZATION_UPDATE))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[OrganizationSettingsResponse]:
    """Update organization configuration settings."""
    svc = OrganizationManagementService(session)
    settings_rec = await svc.update_settings(
        organization_id=tenant.organization_id,
        actor_user_id=tenant.user_id,
        settings_payload=payload.settings_payload,
        correlation_id=str(get_request_id(request)),
    )
    await session.commit()
    await session.refresh(settings_rec)
    return success_response(
        data=OrganizationSettingsResponse.model_validate(settings_rec),
        request_id=get_request_id(request),
    )


@router.get(
    "/{organization_id}/members",
    response_model=EnvelopeResponse[list[OrganizationMemberResponse]],
    summary="List organization members",
)
async def list_organization_members(
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_permission(Permission.ORGANIZATION_READ))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[list[OrganizationMemberResponse]]:
    """List memberships for the organization."""
    svc = MembershipAndInvitationService(session)
    members = await svc.list_members(tenant.organization_id)
    return success_response(
        data=[OrganizationMemberResponse.model_validate(m) for m in members],
        request_id=get_request_id(request),
    )


@router.patch(
    "/{organization_id}/members/{user_id}",
    response_model=EnvelopeResponse[OrganizationMemberResponse],
    summary="Update organization membership",
)
async def update_organization_member(
    user_id: UUID,
    payload: OrganizationMemberUpdateRequest,
    request: Request,
    tenant: Annotated[
        TenantContext, Depends(require_permission(Permission.ORGANIZATION_MANAGE_MEMBERS))
    ],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[OrganizationMemberResponse]:
    """Update member role or status while protecting the final active owner."""
    svc = MembershipAndInvitationService(session)
    try:
        role_enum = OrganizationRole(payload.role) if payload.role else None
        status_enum = MembershipStatus(payload.status) if payload.status else None
        member = await svc.update_member(
            organization_id=tenant.organization_id,
            target_user_id=user_id,
            actor_user_id=tenant.user_id,
            role=role_enum,
            status=status_enum,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(member)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except Exception as exc:
        await session.rollback()
        _handle_domain_error(exc)
        raise

    return success_response(
        data=OrganizationMemberResponse.model_validate(member),
        request_id=get_request_id(request),
    )


@router.delete(
    "/{organization_id}/members/{user_id}",
    response_model=EnvelopeResponse[OrganizationMemberResponse],
    summary="Remove organization membership",
)
async def remove_organization_member(
    user_id: UUID,
    request: Request,
    tenant: Annotated[
        TenantContext, Depends(require_permission(Permission.ORGANIZATION_MANAGE_MEMBERS))
    ],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[OrganizationMemberResponse]:
    """Revoke a member's organization access."""
    svc = MembershipAndInvitationService(session)
    try:
        member = await svc.remove_member(
            organization_id=tenant.organization_id,
            target_user_id=user_id,
            actor_user_id=tenant.user_id,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(member)
    except Exception as exc:
        await session.rollback()
        _handle_domain_error(exc)
        raise

    return success_response(
        data=OrganizationMemberResponse.model_validate(member),
        request_id=get_request_id(request),
    )


@router.post(
    "/{organization_id}/transfer-ownership",
    response_model=EnvelopeResponse[OrganizationMemberResponse],
    summary="Transfer organization ownership",
)
async def transfer_organization_ownership(
    payload: OwnershipTransferRequest,
    request: Request,
    tenant: Annotated[
        TenantContext, Depends(require_permission(Permission.ORGANIZATION_TRANSFER_OWNERSHIP))
    ],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[OrganizationMemberResponse]:
    """Atomically transfer organization ownership to another active member."""
    svc = MembershipAndInvitationService(session)
    try:
        _, new_owner = await svc.transfer_ownership(
            organization_id=tenant.organization_id,
            current_owner_id=tenant.user_id,
            new_owner_id=payload.new_owner_user_id,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(new_owner)
    except Exception as exc:
        await session.rollback()
        _handle_domain_error(exc)
        raise

    return success_response(
        data=OrganizationMemberResponse.model_validate(new_owner),
        request_id=get_request_id(request),
    )


@router.post(
    "/{organization_id}/invitations",
    response_model=EnvelopeResponse[dict[str, object]],
    status_code=status.HTTP_201_CREATED,
    summary="Invite a new member to organization",
)
async def create_invitation(
    payload: InvitationCreateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_permission(Permission.STAFF_INVITE))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[dict[str, object]]:
    """Create a pending invitation with a hashed secure token."""
    svc = MembershipAndInvitationService(session)
    try:
        role_enum = OrganizationRole(payload.role)
        inv, raw_token = await svc.create_invitation(
            organization_id=tenant.organization_id,
            email=payload.email,
            role=role_enum,
            invited_by=tenant.user_id,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(inv)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except Exception as exc:
        await session.rollback()
        _handle_domain_error(exc)
        raise

    inv_dto = InvitationResponse.model_validate(inv).model_dump(mode="json")
    inv_dto["invitation_token"] = raw_token
    return success_response(
        data=inv_dto,
        request_id=get_request_id(request),
    )


@router.get(
    "/{organization_id}/invitations",
    response_model=EnvelopeResponse[list[InvitationResponse]],
    summary="List organization invitations",
)
async def list_invitations(
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_permission(Permission.STAFF_READ))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[list[InvitationResponse]]:
    """List invitations for the organization."""
    svc = MembershipAndInvitationService(session)
    invs = await svc.list_invitations(tenant.organization_id)
    return success_response(
        data=[InvitationResponse.model_validate(i) for i in invs],
        request_id=get_request_id(request),
    )


@router.delete(
    "/{organization_id}/invitations/{invitation_id}",
    response_model=EnvelopeResponse[InvitationResponse],
    summary="Revoke an organization invitation",
)
async def revoke_invitation(
    invitation_id: UUID,
    request: Request,
    tenant: Annotated[
        TenantContext, Depends(require_permission(Permission.ORGANIZATION_MANAGE_MEMBERS))
    ],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[InvitationResponse]:
    """Revoke a pending organization invitation."""
    svc = MembershipAndInvitationService(session)
    try:
        inv = await svc.revoke_invitation(
            organization_id=tenant.organization_id,
            invitation_id=invitation_id,
            actor_user_id=tenant.user_id,
        )
        await session.commit()
        await session.refresh(inv)
    except Exception as exc:
        await session.rollback()
        _handle_domain_error(exc)
        raise

    return success_response(
        data=InvitationResponse.model_validate(inv),
        request_id=get_request_id(request),
    )


@router.post(
    "/{organization_id}/restaurants",
    response_model=EnvelopeResponse[RestaurantSummaryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create restaurant under organization",
)
async def create_org_restaurant(
    payload: CreateRestaurantRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_permission(Permission.RESTAURANT_CREATE))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EnvelopeResponse[RestaurantSummaryResponse]:
    """Create a restaurant owned by the authorized organization."""
    svc = RestaurantManagementService(session)
    try:
        restaurant = await svc.create_restaurant(
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
        await session.refresh(restaurant)
    except Exception as exc:
        await session.rollback()
        _handle_domain_error(exc)
        raise

    return success_response(
        data=RestaurantSummaryResponse.model_validate(restaurant),
        request_id=get_request_id(request),
    )


@router.get(
    "/{organization_id}/restaurants",
    response_model=EnvelopeResponse[PaginatedData[RestaurantSummaryResponse]],
    summary="List restaurants under organization",
)
async def list_org_restaurants(
    request: Request,
    tenant: Annotated[TenantContext, Depends(require_permission(Permission.RESTAURANT_READ))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
) -> EnvelopeResponse[PaginatedData[RestaurantSummaryResponse]]:
    """List paginated restaurants owned by the authorized organization."""
    svc = RestaurantManagementService(session)
    items, total = await svc.list_restaurants(
        organization_id=tenant.organization_id,
        offset=pagination.offset,
        limit=pagination.page_size,
    )
    meta = PaginationMeta.build(
        page=pagination.page,
        page_size=pagination.page_size,
        total_items=total,
    )
    return success_response(
        data=PaginatedData(
            items=[RestaurantSummaryResponse.model_validate(r) for r in items],
            pagination=meta,
        ),
        request_id=get_request_id(request),
    )
