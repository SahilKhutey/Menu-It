"""Branch management and staff assignment API endpoints (FCD-14 §7.3)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.api.dependencies.request_context import get_request_id
from menu_it.api.dependencies.tenant import TenantContext, get_tenant_context_from_request
from menu_it.api.exceptions.responses import success_response
from menu_it.api.schemas.common import APIResponse
from menu_it.authorization.permissions import Permission
from menu_it.authorization.policies import ORGANIZATION_ROLE_PERMISSIONS
from menu_it.database.models.branch import BranchStatus
from menu_it.database.models.branch_assignment import BranchRole
from menu_it.database.session import get_db_session
from menu_it.domain.base.errors import DomainError, EntityNotFoundError
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.schemas.branches import (
    BranchAssignmentResponse,
    BranchAssignmentUpsertRequest,
    BranchResponse,
    BranchUpdateRequest,
)
from menu_it.services.branch_management import BranchManagementService

router = APIRouter(prefix="/branches", tags=["Branches"])


def _check_branch_permission(tenant: TenantContext, permission: Permission) -> None:
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
    if isinstance(exc, DomainError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    raise exc


@router.get(
    "/{branch_id}",
    response_model=APIResponse[BranchResponse],
    summary="Get branch details",
)
async def get_branch(
    branch_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[BranchResponse]:
    """Get branch details scoped to active organization."""
    _check_branch_permission(tenant, Permission.BRANCH_READ)
    svc = BranchManagementService(session)
    try:
        branch = await svc.get_branch(organization_id=tenant.organization_id, branch_id=branch_id)
    except Exception as exc:
        _handle_error(exc)
        raise

    return success_response(
        data=BranchResponse.model_validate(branch),
        request_id=get_request_id(request),
    )


@router.patch(
    "/{branch_id}",
    response_model=APIResponse[BranchResponse],
    summary="Update branch details",
)
async def update_branch(
    branch_id: UUID,
    payload: BranchUpdateRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[BranchResponse]:
    """Update branch operational details and address."""
    _check_branch_permission(tenant, Permission.BRANCH_UPDATE)
    svc = BranchManagementService(session)
    try:
        branch = await svc.update_branch(
            organization_id=tenant.organization_id,
            branch_id=branch_id,
            actor_user_id=tenant.user_id,
            name=payload.name,
            branch_code=payload.branch_code,
            email=payload.email,
            phone=payload.phone,
            address_line_1=payload.address_line_1,
            address_line_2=payload.address_line_2,
            city=payload.city,
            state_region=payload.state_region,
            postal_code=payload.postal_code,
            country_code=payload.country_code,
            timezone=payload.timezone,
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


@router.post(
    "/{branch_id}/activate",
    response_model=APIResponse[BranchResponse],
    summary="Activate branch",
)
async def activate_branch(
    branch_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[BranchResponse]:
    """Activate a suspended or inactive branch."""
    _check_branch_permission(tenant, Permission.BRANCH_UPDATE)
    svc = BranchManagementService(session)
    try:
        branch = await svc.transition_status(
            organization_id=tenant.organization_id,
            branch_id=branch_id,
            target_status=BranchStatus.ACTIVE,
            actor_user_id=tenant.user_id,
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


@router.post(
    "/{branch_id}/suspend",
    response_model=APIResponse[BranchResponse],
    summary="Suspend branch",
)
async def suspend_branch(
    branch_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[BranchResponse]:
    """Suspend an active branch."""
    _check_branch_permission(tenant, Permission.BRANCH_UPDATE)
    svc = BranchManagementService(session)
    try:
        branch = await svc.transition_status(
            organization_id=tenant.organization_id,
            branch_id=branch_id,
            target_status=BranchStatus.SUSPENDED,
            actor_user_id=tenant.user_id,
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
    "/{branch_id}/assignments",
    response_model=APIResponse[list[BranchAssignmentResponse]],
    summary="List branch staff assignments",
)
async def list_branch_assignments(
    branch_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[list[BranchAssignmentResponse]]:
    """List all staff assignments for a branch."""
    _check_branch_permission(tenant, Permission.BRANCH_READ)
    svc = BranchManagementService(session)
    try:
        items = await svc.list_assignments(
            organization_id=tenant.organization_id, branch_id=branch_id
        )
    except Exception as exc:
        _handle_error(exc)
        raise

    return success_response(
        data=[BranchAssignmentResponse.model_validate(a) for a in items],
        request_id=get_request_id(request),
    )


@router.put(
    "/{branch_id}/assignments/{user_id}",
    response_model=APIResponse[BranchAssignmentResponse],
    summary="Assign or update user branch role",
)
async def upsert_branch_assignment(
    branch_id: UUID,
    user_id: UUID,
    payload: BranchAssignmentUpsertRequest,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[BranchAssignmentResponse]:
    """Assign an organization member to a specific branch."""
    _check_branch_permission(tenant, Permission.BRANCH_MANAGE_ASSIGNMENTS)
    svc = BranchManagementService(session)
    try:
        role_enum = BranchRole(payload.role)
        assignment = await svc.upsert_assignment(
            organization_id=tenant.organization_id,
            branch_id=branch_id,
            user_id=user_id,
            role=role_enum,
            actor_user_id=tenant.user_id,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
        await session.refresh(assignment)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except Exception as exc:
        await session.rollback()
        _handle_error(exc)
        raise

    return success_response(
        data=BranchAssignmentResponse.model_validate(assignment),
        request_id=get_request_id(request),
    )


@router.delete(
    "/{branch_id}/assignments/{user_id}",
    response_model=APIResponse[dict[str, str]],
    summary="Remove user branch assignment",
)
async def remove_branch_assignment(
    branch_id: UUID,
    user_id: UUID,
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> APIResponse[dict[str, str]]:
    """Remove a user's assignment from a branch."""
    _check_branch_permission(tenant, Permission.BRANCH_MANAGE_ASSIGNMENTS)
    svc = BranchManagementService(session)
    try:
        await svc.remove_assignment(
            organization_id=tenant.organization_id,
            branch_id=branch_id,
            user_id=user_id,
            actor_user_id=tenant.user_id,
            correlation_id=str(get_request_id(request)),
        )
        await session.commit()
    except Exception as exc:
        await session.rollback()
        _handle_error(exc)
        raise

    return success_response(
        data={"status": "removed", "branch_id": str(branch_id), "user_id": str(user_id)},
        request_id=get_request_id(request),
    )
