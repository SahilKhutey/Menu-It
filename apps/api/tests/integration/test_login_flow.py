"""Integration tests for login verification, lockout, and status handling (FCD-05 §7, §22)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.exceptions import (
    AccountLockedError,
    AccountNotActiveError,
    AccountSuspendedError,
    InvalidCredentialsError,
)
from menu_it.authentication.service import AuthenticationService
from menu_it.database.models.session import SessionStatus
from menu_it.database.models.user import UserStatus


@pytest.mark.asyncio
async def test_login_success_issues_tokens_and_session(db_session: AsyncSession):
    """Verify correct credentials issue access JWT and active user session."""
    auth_service = AuthenticationService(db_session)
    password = "Correct-password-123456"

    user, _ = await auth_service.register(
        email="login_user@example.com",
        display_name="Login User",
        password=password,
    )
    user.status = UserStatus.ACTIVE
    user.email_verified = True
    await db_session.commit()

    logged_user, session, access_token, refresh_token = await auth_service.login(
        email="login_user@example.com",
        password=password,
        ip_address="192.168.1.10",
        user_agent="Mozilla/5.0 Test",
    )
    await db_session.commit()

    assert logged_user.id == user.id
    assert session.id is not None
    assert session.status == SessionStatus.ACTIVE
    assert session.ip_address == "192.168.1.10"
    assert session.user_agent == "Mozilla/5.0 Test"
    assert len(access_token) > 50
    assert len(refresh_token) >= 64


@pytest.mark.asyncio
async def test_login_invalid_password_fails(db_session: AsyncSession):
    """Verify incorrect password raises InvalidCredentialsError."""
    auth_service = AuthenticationService(db_session)
    password = "Correct-password-123456"

    user, _ = await auth_service.register(
        email="fail_user@example.com",
        display_name="Fail User",
        password=password,
    )
    user.status = UserStatus.ACTIVE
    await db_session.commit()

    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(
            email="fail_user@example.com",
            password="Wrong-password-9999",
        )


@pytest.mark.asyncio
async def test_repeated_login_failures_locks_account(db_session: AsyncSession):
    """Verify 5 failed attempts trigger account lockout (FCD-05 §2.1)."""
    auth_service = AuthenticationService(db_session)
    password = "Correct-password-123456"

    user, _ = await auth_service.register(
        email="lock_user@example.com",
        display_name="Lock User",
        password=password,
    )
    user.status = UserStatus.ACTIVE
    await db_session.commit()

    # Attempt 4 failed logins
    for _ in range(4):
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login(
                email="lock_user@example.com",
                password="Wrong-password-9999",
            )
        await db_session.commit()

    # 5th failed attempt triggers lockout
    with pytest.raises(AccountLockedError):
        await auth_service.login(
            email="lock_user@example.com",
            password="Wrong-password-9999",
        )
    await db_session.commit()

    # Account remains locked even with correct password
    with pytest.raises(AccountLockedError, match="temporarily locked"):
        await auth_service.login(
            email="lock_user@example.com",
            password=password,
        )


@pytest.mark.asyncio
async def test_suspended_and_deactivated_login_rejected(db_session: AsyncSession):
    """Verify suspended and deactivated accounts cannot authenticate."""
    auth_service = AuthenticationService(db_session)
    password = "Correct-password-123456"

    user, _ = await auth_service.register(
        email="suspended@example.com",
        display_name="Suspended User",
        password=password,
    )
    user.status = UserStatus.SUSPENDED
    await db_session.commit()

    with pytest.raises(AccountSuspendedError):
        await auth_service.login(
            email="suspended@example.com",
            password=password,
        )

    user.status = UserStatus.DEACTIVATED
    await db_session.commit()

    with pytest.raises(AccountNotActiveError):
        await auth_service.login(
            email="suspended@example.com",
            password=password,
        )
