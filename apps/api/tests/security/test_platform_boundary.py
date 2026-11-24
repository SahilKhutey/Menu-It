"""Security tests verifying platform administrative privilege separation (FCD-05 §15, §17)."""

from uuid import uuid4

import pytest
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.tokens import create_access_token
from menu_it.authorization.dependencies import require_platform_role
from menu_it.core.config import get_settings
from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationMembership,
    OrganizationRole,
)
from menu_it.database.models.platform import (
    PlatformMembership,
    PlatformMembershipStatus,
    PlatformRole,
)
from menu_it.database.models.user import User, UserStatus
from menu_it.sessions.service import SessionService

dummy_platform_router = APIRouter(prefix="/test/platform")


@dummy_platform_router.get("/admin-only")
async def admin_only_endpoint(
    membership: PlatformMembership = Depends(require_platform_role(PlatformRole.PLATFORM_ADMIN)),
) -> dict[str, str]:
    return {"status": "ok", "role": membership.role.value}


@dummy_platform_router.get("/support-or-admin")
async def support_or_admin_endpoint(
    membership: PlatformMembership = Depends(
        require_platform_role(PlatformRole.PLATFORM_ADMIN, PlatformRole.PLATFORM_SUPPORT)
    ),
) -> dict[str, str]:
    return {"status": "ok", "role": membership.role.value}


@pytest.mark.asyncio
async def test_platform_admin_access_granted(
    authed_client,
    app,
    db_session: AsyncSession,
) -> None:
    """User with active PLATFORM_ADMIN membership can access platform admin endpoint."""
    app.include_router(dummy_platform_router)
    settings = get_settings()

    user = User(
        email="platform_admin@example.com",
        normalized_email="platform_admin@example.com",
        display_name="Platform Admin",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    platform_membership = PlatformMembership(
        user_id=user.id,
        role=PlatformRole.PLATFORM_ADMIN,
        status=PlatformMembershipStatus.ACTIVE,
    )
    db_session.add(platform_membership)
    await db_session.flush()

    session_service = SessionService(db_session)
    session, _ = await session_service.create_session(user_id=user.id)
    await db_session.commit()

    token = create_access_token(
        user_id=user.id,
        session_id=session.id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=900,
    )

    response = authed_client.get(
        "/test/platform/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "platform_admin"


@pytest.mark.asyncio
async def test_tenant_owner_cannot_access_platform_endpoints(
    authed_client,
    app,
    db_session: AsyncSession,
) -> None:
    """An organization owner without platform membership is forbidden from platform endpoints."""
    app.include_router(dummy_platform_router)
    settings = get_settings()

    org = Organization(
        name="Big Tenant",
        slug=f"big-tenant-{uuid4().hex[:6]}",
        status=OrganizationStatus.ACTIVE,
    )
    user = User(
        email="tenant_owner@example.com",
        normalized_email="tenant_owner@example.com",
        display_name="Tenant Owner",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add_all([org, user])
    await db_session.flush()

    org_membership = OrganizationMembership(
        organization_id=org.id,
        user_id=user.id,
        role=OrganizationRole.OWNER,
        status=MembershipStatus.ACTIVE,
    )
    db_session.add(org_membership)
    await db_session.flush()

    session_service = SessionService(db_session)
    session, _ = await session_service.create_session(user_id=user.id)
    await db_session.commit()

    token = create_access_token(
        user_id=user.id,
        session_id=session.id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=900,
    )

    response = authed_client.get(
        "/test/platform/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert "platform administrative privilege required" in response.text.lower()


@pytest.mark.asyncio
async def test_suspended_platform_membership_denied(
    authed_client,
    app,
    db_session: AsyncSession,
) -> None:
    """Suspended platform membership denies administrative access."""
    app.include_router(dummy_platform_router)
    settings = get_settings()

    user = User(
        email="suspended_admin@example.com",
        normalized_email="suspended_admin@example.com",
        display_name="Suspended Admin",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    platform_membership = PlatformMembership(
        user_id=user.id,
        role=PlatformRole.PLATFORM_ADMIN,
        status=PlatformMembershipStatus.SUSPENDED,
    )
    db_session.add(platform_membership)
    await db_session.flush()

    session_service = SessionService(db_session)
    session, _ = await session_service.create_session(user_id=user.id)
    await db_session.commit()

    token = create_access_token(
        user_id=user.id,
        session_id=session.id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=900,
    )

    response = authed_client.get(
        "/test/platform/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
