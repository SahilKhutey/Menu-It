"""Integration tests for FCD-05 authentication integrated with FCD-04 multi-tenancy."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.tokens import create_access_token
from menu_it.core.config import get_settings
from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationMembership,
    OrganizationRole,
)
from menu_it.database.models.user import User, UserStatus
from menu_it.sessions.service import SessionService


@pytest.mark.asyncio
async def test_tenant_access_with_bearer_jwt(
    authed_client,
    db_session: AsyncSession,
) -> None:
    """Authenticated user with valid session and org membership accesses tenant endpoints."""
    settings = get_settings()

    # 1. Create Organization
    org = Organization(
        name="Acme Foods",
        slug=f"acme-foods-{uuid4().hex[:6]}",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org)
    await db_session.flush()

    # 2. Create User
    user = User(
        email="owner@acme.com",
        normalized_email="owner@acme.com",
        display_name="Acme Owner",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    # 3. Create Membership (Owner)
    membership = OrganizationMembership(
        organization_id=org.id,
        user_id=user.id,
        role=OrganizationRole.OWNER,
        status=MembershipStatus.ACTIVE,
    )
    db_session.add(membership)
    await db_session.flush()

    # 4. Create Active Session
    session_service = SessionService(db_session)
    session, _ = await session_service.create_session(user_id=user.id)
    await db_session.commit()

    # 5. Issue Access Token
    token = create_access_token(
        user_id=user.id,
        session_id=session.id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=900,
    )

    # 6. Request organization access summary
    headers = {"Authorization": f"Bearer {token}"}
    response = authed_client.get(
        f"/api/v1/organizations/{org.id}/access",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["organization_id"] == str(org.id)
    assert body["data"]["user_id"] == str(user.id)
    assert body["data"]["organization_role"] == "owner"
    assert "organization:read" in body["data"]["permissions"]
    assert "organization:manage_members" in body["data"]["permissions"]


@pytest.mark.asyncio
async def test_tenant_access_forbidden_without_membership(
    authed_client,
    db_session: AsyncSession,
) -> None:
    """User without membership in requested organization is rejected with 404."""
    settings = get_settings()

    # 1. Organization A and User
    org = Organization(
        name="Other Org",
        slug=f"other-org-{uuid4().hex[:6]}",
        status=OrganizationStatus.ACTIVE,
    )
    user = User(
        email="outsider@example.com",
        normalized_email="outsider@example.com",
        display_name="Outsider",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add_all([org, user])
    await db_session.flush()

    # 2. Session for User (no membership in org)
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

    headers = {"Authorization": f"Bearer {token}"}
    response = authed_client.get(
        f"/api/v1/organizations/{org.id}/access",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_tenant_access_rejected_when_session_revoked(
    authed_client,
    db_session: AsyncSession,
) -> None:
    """An access token whose session has been revoked in the DB is rejected with 401."""
    settings = get_settings()

    org = Organization(
        name="Revoked Corp",
        slug=f"revoked-{uuid4().hex[:6]}",
        status=OrganizationStatus.ACTIVE,
    )
    user = User(
        email="revoked_sess@example.com",
        normalized_email="revoked_sess@example.com",
        display_name="Revoked User",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add_all([org, user])
    await db_session.flush()

    membership = OrganizationMembership(
        organization_id=org.id,
        user_id=user.id,
        role=OrganizationRole.STAFF,
        status=MembershipStatus.ACTIVE,
    )
    db_session.add(membership)
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

    # Revoke session
    await session_service.revoke_session(user.id, session.id)
    await db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    response = authed_client.get(
        f"/api/v1/organizations/{org.id}/access",
        headers=headers,
    )
    assert response.status_code == 401
    assert "revoked" in response.text.lower()
