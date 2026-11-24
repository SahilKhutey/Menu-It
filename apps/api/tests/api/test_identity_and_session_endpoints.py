"""API tests for identity profile and session management endpoints (FCD-05 §18)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.tokens import create_access_token
from menu_it.core.config import get_settings
from menu_it.database.models.user import User, UserStatus
from menu_it.sessions.service import SessionService


@pytest.mark.asyncio
async def test_identity_me_endpoints(authed_client, db_session: AsyncSession) -> None:
    """GET and PATCH /api/v1/identity/me retrieves and updates current user profile."""
    settings = get_settings()

    user = User(
        email="identity_me@example.com",
        normalized_email="identity_me@example.com",
        display_name="Original Name",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
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
        ttl_seconds=600,
    )

    headers = {"Authorization": f"Bearer {token}"}

    # 1. GET /api/v1/identity/me
    get_res = authed_client.get("/api/v1/identity/me", headers=headers)
    assert get_res.status_code == 200
    data = get_res.json()["data"]
    assert data["email"] == "identity_me@example.com"
    assert data["display_name"] == "Original Name"

    # 2. PATCH /api/v1/identity/me
    patch_res = authed_client.patch(
        "/api/v1/identity/me",
        headers=headers,
        json={"display_name": "Updated Profile Name"},
    )
    assert patch_res.status_code == 200
    updated_data = patch_res.json()["data"]
    assert updated_data["display_name"] == "Updated Profile Name"


@pytest.mark.asyncio
async def test_session_management_endpoints(
    authed_client,
    db_session: AsyncSession,
) -> None:
    """GET and DELETE /api/v1/sessions allows listing and revoking active user devices."""
    settings = get_settings()

    user = User(
        email="session_mgmt@example.com",
        normalized_email="session_mgmt@example.com",
        display_name="Session Mgmt User",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    session_service = SessionService(db_session)
    s1, _ = await session_service.create_session(
        user_id=user.id,
        user_agent="Device A (Laptop)",
        ip_address="192.168.1.5",
    )
    s2, _ = await session_service.create_session(
        user_id=user.id,
        user_agent="Device B (Phone)",
        ip_address="192.168.1.10",
    )
    await db_session.commit()

    token = create_access_token(
        user_id=user.id,
        session_id=s1.id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=600,
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List active sessions
    list_res = authed_client.get("/api/v1/sessions", headers=headers)
    assert list_res.status_code == 200
    sessions_list = list_res.json()["data"]
    assert len(sessions_list) == 2
    session_ids = [s["id"] for s in sessions_list]
    assert str(s1.id) in session_ids
    assert str(s2.id) in session_ids

    # 2. Revoke session 2
    del_res = authed_client.delete(f"/api/v1/sessions/{s2.id}", headers=headers)
    assert del_res.status_code == 200

    # 3. List again -> only session 1 active
    list_after = authed_client.get("/api/v1/sessions", headers=headers)
    assert list_after.status_code == 200
    active_after = list_after.json()["data"]
    assert len(active_after) == 1
    assert active_after[0]["id"] == str(s1.id)
