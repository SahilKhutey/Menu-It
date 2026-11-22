"""
ModularMenu — Organization & Tenancy API Endpoints (ARC-07 §4.2).
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authentication import AuthenticatedActor, get_current_actor
from app.api.dependencies.authorization import require_permission
from app.api.schemas.organizations import (
    InvitationCreateRequest,
    InvitationResponse,
    OrganizationCreateRequest,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from app.core.database import get_db
from app.modules.identity.models import Organization, RestaurantMember
from app.shared.application.tenant_context import TenantContext

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("", response_model=list[OrganizationResponse])
async def list_user_organizations(
    actor: AuthenticatedActor = Depends(get_current_actor),
    db: AsyncSession = Depends(get_db),
):
    """Lists organizations that the authenticated user belongs to."""
    if actor.is_platform_admin:
        result = await db.execute(select(Organization).order_by(Organization.name.asc()))
        return result.scalars().all()

    # Query via RestaurantMember or OrganizationMember
    stmt = (
        select(Organization)
        .join(RestaurantMember, RestaurantMember.organization_id == Organization.id)
        .where(RestaurantMember.user_id == actor.user_id)
        .distinct()
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreateRequest,
    actor: AuthenticatedActor = Depends(get_current_actor),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new organization tenant and grants owner membership."""
    existing = await db.execute(select(Organization).where(Organization.slug == payload.slug))
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Organization with slug '{payload.slug}' already exists",
        )

    new_org = Organization(
        name=payload.name,
        slug=payload.slug,
        status="active",
        country_code=payload.country_code,
        default_currency=payload.default_currency,
    )
    db.add(new_org)
    await db.flush()

    # Grant owner membership
    owner_member = RestaurantMember(
        organization_id=new_org.id,
        user_id=actor.user_id,
        role="owner",
    )
    db.add(owner_member)
    await db.commit()
    await db.refresh(new_org)
    return new_org


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: uuid.UUID,
    actor: AuthenticatedActor = Depends(get_current_actor),
    tenant: TenantContext = Depends(require_permission("organization.read")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves organization details within the authorized tenant scope."""
    if tenant.organization_id != organization_id and not actor.is_platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    result = await db.execute(select(Organization).where(Organization.id == organization_id))
    org = result.scalars().first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: uuid.UUID,
    payload: OrganizationUpdateRequest,
    actor: AuthenticatedActor = Depends(get_current_actor),
    tenant: TenantContext = Depends(require_permission("organization.update")),
    db: AsyncSession = Depends(get_db),
):
    """Updates organization profile."""
    if tenant.organization_id != organization_id and not actor.is_platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    result = await db.execute(select(Organization).where(Organization.id == organization_id))
    org = result.scalars().first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(org, field, val)

    await db.commit()
    await db.refresh(org)
    return org


@router.get("/{organization_id}/members", response_model=list[OrganizationMemberResponse])
async def list_organization_members(
    organization_id: uuid.UUID,
    actor: AuthenticatedActor = Depends(get_current_actor),
    tenant: TenantContext = Depends(require_permission("organization.members.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Lists all members of the specified organization."""
    if tenant.organization_id != organization_id and not actor.is_platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    stmt = select(RestaurantMember).where(RestaurantMember.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/{organization_id}/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_member(
    organization_id: uuid.UUID,
    payload: InvitationCreateRequest,
    actor: AuthenticatedActor = Depends(get_current_actor),
    tenant: TenantContext = Depends(require_permission("organization.members.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Issues an invitation to join the organization."""
    if tenant.organization_id != organization_id and not actor.is_platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    import datetime

    expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
    invitation = {
        "id": uuid.uuid4(),
        "organization_id": organization_id,
        "email": payload.email,
        "role": payload.role,
        "status": "pending",
        "expires_at": expires_at,
        "created_at": datetime.datetime.now(datetime.UTC),
    }
    return invitation


@router.delete("/{organization_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_organization_member(
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    actor: AuthenticatedActor = Depends(get_current_actor),
    tenant: TenantContext = Depends(require_permission("organization.members.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Removes a user's membership from the organization."""
    if tenant.organization_id != organization_id and not actor.is_platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if user_id == tenant.user_id and tenant.is_owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove organization owner"
        )

    stmt = select(RestaurantMember).where(
        RestaurantMember.organization_id == organization_id,
        RestaurantMember.user_id == user_id,
    )
    result = await db.execute(stmt)
    member = result.scalars().first()
    if member:
        await db.delete(member)
        await db.commit()
    return None
