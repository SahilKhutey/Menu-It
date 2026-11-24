"""Integration tests for password recovery and reset workflow (FCD-05 §11)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.credentials.hashing import hash_password, verify_password
from menu_it.credentials.repository import CredentialRepository
from menu_it.database.models.session import SessionStatus
from menu_it.database.models.user import User, UserStatus
from menu_it.recovery.exceptions import InvalidRecoveryTokenError
from menu_it.recovery.service import PasswordRecoveryService
from menu_it.sessions.service import SessionService


@pytest.mark.asyncio
async def test_password_recovery_success(db_session: AsyncSession) -> None:
    """Password recovery resets hash, unlocks account, and revokes all active sessions."""
    user = User(
        email="recover_me@example.com",
        normalized_email="recover_me@example.com",
        display_name="Recover Candidate",
        status=UserStatus.LOCKED,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    cred_repo = CredentialRepository(db_session)
    old_hash = hash_password("OldSecurePass123!_")
    await cred_repo.set_password_hash(user.id, old_hash)

    # User had 2 active sessions
    session_service = SessionService(db_session)
    s1, _ = await session_service.create_session(user_id=user.id)
    s2, _ = await session_service.create_session(user_id=user.id)
    await db_session.commit()

    recovery_service = PasswordRecoveryService(db_session)
    raw_token = await recovery_service.create_password_reset_token("recover_me@example.com")
    assert raw_token is not None
    await db_session.commit()

    # Reset with new password
    updated_user = await recovery_service.reset_password(
        raw_token,
        "NewVerySecurePassword456!@",
    )
    await db_session.commit()

    assert updated_user.status == UserStatus.ACTIVE
    assert updated_user.failed_login_attempts == 0
    assert updated_user.locked_until is None

    # Check new credential verifies
    new_cred = await cred_repo.get_by_user_id(user.id)
    assert new_cred is not None
    assert verify_password(new_cred.password_hash, "NewVerySecurePassword456!@") is True
    assert verify_password(new_cred.password_hash, "OldSecurePass123!_") is False
    assert verify_password("OldSecurePass123!_", new_cred.password_hash) is False

    # Check both sessions are revoked
    s1_reloaded = await session_service.repository.get_by_id(s1.id)
    s2_reloaded = await session_service.repository.get_by_id(s2.id)
    assert s1_reloaded.status == SessionStatus.REVOKED
    assert s2_reloaded.status == SessionStatus.REVOKED


@pytest.mark.asyncio
async def test_password_recovery_consumed_token_fails(db_session: AsyncSession) -> None:
    """A reset token cannot be used twice."""
    user = User(
        email="recover_once@example.com",
        normalized_email="recover_once@example.com",
        display_name="Recover Once",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    cred_repo = CredentialRepository(db_session)
    await cred_repo.set_password_hash(user.id, hash_password("StartingPass123!#"))
    await db_session.commit()

    recovery_service = PasswordRecoveryService(db_session)
    raw_token = await recovery_service.create_password_reset_token("recover_once@example.com")
    assert raw_token is not None
    await db_session.commit()

    await recovery_service.reset_password(raw_token, "FirstNewPass123!@")
    await db_session.commit()

    with pytest.raises(InvalidRecoveryTokenError) as exc:
        await recovery_service.reset_password(raw_token, "SecondNewPass456!$")
    assert "already been used" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_password_recovery_expired_token_fails(db_session: AsyncSession) -> None:
    """An expired reset token is rejected."""
    user = User(
        email="recover_exp@example.com",
        normalized_email="recover_exp@example.com",
        display_name="Recover Expired",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    cred_repo = CredentialRepository(db_session)
    await cred_repo.set_password_hash(user.id, hash_password("StartingPass123!#"))
    await db_session.commit()

    recovery_service = PasswordRecoveryService(db_session)
    raw_token = await recovery_service.create_password_reset_token(
        "recover_exp@example.com",
        ttl_seconds=-10,
    )
    assert raw_token is not None
    await db_session.commit()

    with pytest.raises(InvalidRecoveryTokenError) as exc:
        await recovery_service.reset_password(raw_token, "ValidNewPass123!@")
    assert "expired" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_password_recovery_rejects_weak_password(db_session: AsyncSession) -> None:
    """Resetting to a weak password fails password policy validation."""
    recovery_service = PasswordRecoveryService(db_session)
    with pytest.raises(ValueError) as exc:
        await recovery_service.reset_password("dummy-token", "short")
    assert "at least 12 characters" in str(exc.value)
