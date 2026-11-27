"""API endpoint integration tests for authentication workflows (FCD-05 §18)."""

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.user import User, UserStatus


@pytest.mark.asyncio
async def test_auth_registration_endpoint(authed_client) -> None:
    """POST /api/v1/auth/register creates user account in pending verification status."""
    email = f"api_user_{uuid4().hex[:6]}@example.com"
    response = authed_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!@",
            "display_name": "API New User",
        },
    )
    assert response.status_code == 202
    data = response.json()["data"]
    assert data["email"] == email
    assert data["status"] == "pending_verification"
    assert data["email_verified"] is False

    # Duplicate registration returns 409
    dup_response = authed_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!@",
            "display_name": "Duplicate User",
        },
    )
    assert dup_response.status_code == 409


@pytest.mark.asyncio
async def test_auth_login_endpoint(authed_client, db_session: AsyncSession) -> None:
    """POST /api/v1/auth/login verifies credentials, issues JWT access token and refresh cookie."""
    # Register and activate user
    email = f"login_user_{uuid4().hex[:6]}@example.com"
    reg_res = authed_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SuperSecretPass123!$",
            "display_name": "Login Test User",
        },
    )
    assert reg_res.status_code == 202

    # Activate user in database
    stmt = select(User).where(User.email == email)
    res = await db_session.execute(stmt)
    user = res.scalar_one()
    user.status = UserStatus.ACTIVE
    user.email_verified = True
    await db_session.commit()

    # Login
    login_res = authed_client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "SuperSecretPass123!$",
        },
    )
    assert login_res.status_code == 200
    body = login_res.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["token_type"] == "Bearer"
    assert body["data"]["expires_in"] == 600
    assert "menu_it_refresh" in login_res.cookies


@pytest.mark.asyncio
async def test_auth_refresh_endpoint(authed_client, db_session: AsyncSession) -> None:
    """POST /api/v1/auth/refresh rotates refresh token and returns fresh access token."""
    email = f"refresh_api_{uuid4().hex[:6]}@example.com"
    authed_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SuperSecretPass123!$",
            "display_name": "Refresh User",
        },
    )
    stmt = select(User).where(User.email == email)
    res = await db_session.execute(stmt)
    user = res.scalar_one()
    user.status = UserStatus.ACTIVE
    user.email_verified = True
    await db_session.commit()

    login_res = authed_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SuperSecretPass123!$"},
    )
    assert login_res.status_code == 200
    initial_refresh = login_res.cookies.get("menu_it_refresh")

    # Refresh using cookie
    refresh_res = authed_client.post("/api/v1/auth/refresh")
    assert refresh_res.status_code == 200
    body = refresh_res.json()
    assert "access_token" in body["data"]

    new_refresh = refresh_res.cookies.get("menu_it_refresh")
    assert new_refresh is not None
    assert new_refresh != initial_refresh


@pytest.mark.asyncio
async def test_auth_logout_endpoint(authed_client, db_session: AsyncSession) -> None:
    """POST /api/v1/auth/logout revokes current session and clears refresh cookie."""
    email = f"logout_api_{uuid4().hex[:6]}@example.com"
    authed_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SuperSecretPass123!$",
            "display_name": "Logout User",
        },
    )
    stmt = select(User).where(User.email == email)
    res = await db_session.execute(stmt)
    user = res.scalar_one()
    user.status = UserStatus.ACTIVE
    user.email_verified = True
    await db_session.commit()

    login_res = authed_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SuperSecretPass123!$"},
    )
    access_token = login_res.json()["data"]["access_token"]

    logout_res = authed_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["success"] is True

    # Subsequent refresh with cleared cookie must fail
    follow_up_refresh = authed_client.post("/api/v1/auth/refresh")
    assert follow_up_refresh.status_code == 401


@pytest.mark.asyncio
async def test_auth_logout_all_endpoint(authed_client, db_session: AsyncSession) -> None:
    """POST /api/v1/auth/logout-all revokes all sessions across devices."""
    email = f"logoutall_{uuid4().hex[:6]}@example.com"
    authed_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SuperSecretPass123!$", "display_name": "LogoutAll User"},
    )
    stmt = select(User).where(User.email == email)
    res = await db_session.execute(stmt)
    user = res.scalar_one()
    user.status = UserStatus.ACTIVE
    user.email_verified = True
    await db_session.commit()

    login_res = authed_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SuperSecretPass123!$"},
    )
    token = login_res.json()["data"]["access_token"]

    res = authed_client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["revoked_sessions"] >= 1


@pytest.mark.asyncio
async def test_auth_email_verification_and_resend_endpoints(
    authed_client,
    db_session: AsyncSession,
) -> None:
    """POST /email/resend and /email/verify activate unverified account."""
    from menu_it.verification.service import EmailVerificationService

    email = f"verif_api_{uuid4().hex[:6]}@example.com"
    authed_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SuperSecretPass123!$", "display_name": "Verif User"},
    )

    # Resend endpoint returns success message
    resend_res = authed_client.post(
        "/api/v1/auth/email/resend",
        json={"email": email},
    )
    assert resend_res.status_code == 200

    # Retrieve issued token
    stmt = select(User).where(User.email == email)
    res = await db_session.execute(stmt)
    user = res.scalar_one()
    verif_svc = EmailVerificationService(db_session)
    raw_token = await verif_svc.create_verification_token(user.id)
    await db_session.commit()

    # Call verify endpoint
    verif_res = authed_client.post(
        "/api/v1/auth/email/verify",
        json={"token": raw_token},
    )
    assert verif_res.status_code == 200
    assert verif_res.json()["data"]["email_verified"] is True
    assert verif_res.json()["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_auth_password_forgot_and_reset_endpoints(
    authed_client,
    db_session: AsyncSession,
) -> None:
    """POST /api/v1/auth/password/forgot and /reset complete password recovery."""
    from menu_it.recovery.service import PasswordRecoveryService

    email = f"reset_api_{uuid4().hex[:6]}@example.com"
    authed_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SuperSecretPass123!$", "display_name": "Reset User"},
    )
    stmt = select(User).where(User.email == email)
    res = await db_session.execute(stmt)
    user = res.scalar_one()
    user.status = UserStatus.ACTIVE
    user.email_verified = True
    await db_session.commit()

    forgot_res = authed_client.post(
        "/api/v1/auth/password/forgot",
        json={"email": email},
    )
    assert forgot_res.status_code == 200

    recovery_svc = PasswordRecoveryService(db_session)
    raw_token = await recovery_svc.create_password_reset_token(email)
    assert raw_token is not None
    await db_session.commit()

    reset_res = authed_client.post(
        "/api/v1/auth/password/reset",
        json={"token": raw_token, "new_password": "CompletelyNewSecret123!@"},
    )
    assert reset_res.status_code == 200

    # Login with new password succeeds
    login_res = authed_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "CompletelyNewSecret123!@"},
    )
    assert login_res.status_code == 200


@pytest.mark.asyncio
async def test_auth_password_change_endpoint(
    authed_client,
    db_session: AsyncSession,
) -> None:
    """POST /api/v1/auth/password/change verifies current password and updates to new password."""
    email = f"change_api_{uuid4().hex[:6]}@example.com"
    authed_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "InitialSecret123!$", "display_name": "Change User"},
    )
    stmt = select(User).where(User.email == email)
    res = await db_session.execute(stmt)
    user = res.scalar_one()
    user.status = UserStatus.ACTIVE
    user.email_verified = True
    await db_session.commit()

    login_res = authed_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "InitialSecret123!$"},
    )
    token = login_res.json()["data"]["access_token"]

    change_res = authed_client.post(
        "/api/v1/auth/password/change",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "InitialSecret123!$",
            "new_password": "UpdatedSecret456!#",
        },
    )
    assert change_res.status_code == 200
