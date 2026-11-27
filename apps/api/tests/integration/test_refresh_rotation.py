"""Integration tests for refresh token rotation and reuse detection (FCD-05 §8.4, §9.3)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.session import SessionStatus
from menu_it.database.models.user import User, UserStatus
from menu_it.sessions.exceptions import (
    InvalidRefreshTokenError,
    SessionRevokedError,
    TokenReuseDetectedError,
)
from menu_it.sessions.service import SessionService


@pytest.mark.asyncio
async def test_successful_refresh_rotation(db_session: AsyncSession) -> None:
    """Rotating a valid refresh token issues new tokens and consumes the old one."""
    user = User(
        email="rotate@example.com",
        normalized_email="rotate@example.com",
        display_name="Rotate User",
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    await db_session.flush()

    session_service = SessionService(db_session)
    session, initial_refresh = await session_service.create_session(user_id=user.id)
    await db_session.commit()

    # Rotate token
    updated_session, new_refresh = await session_service.rotate_refresh_token(initial_refresh)
    await db_session.commit()

    assert updated_session.id == session.id
    assert new_refresh != initial_refresh
    assert updated_session.status == SessionStatus.ACTIVE

    # Verify old token cannot be reused normally
    with pytest.raises(TokenReuseDetectedError):
        await session_service.rotate_refresh_token(initial_refresh)


@pytest.mark.asyncio
async def test_refresh_token_reuse_detection_revokes_family_and_session(
    db_session: AsyncSession,
) -> None:
    """When a consumed refresh token is presented again, reuse detection triggers:
    the entire family is revoked and the session is terminated.
    """
    user = User(
        email="reuse@example.com",
        normalized_email="reuse@example.com",
        display_name="Reuse Attacker",
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    await db_session.flush()

    session_service = SessionService(db_session)
    session, token_1 = await session_service.create_session(user_id=user.id)
    await db_session.commit()

    # Legitimate client rotates token_1 -> gets token_2
    _, token_2 = await session_service.rotate_refresh_token(token_1)
    await db_session.commit()

    # Attacker or replay presents token_1 again
    with pytest.raises(TokenReuseDetectedError) as exc_info:
        await session_service.rotate_refresh_token(token_1)
    await db_session.commit()

    assert "reuse detected" in str(exc_info.value).lower()

    # Verify the session is now REVOKED
    validated = await session_service.validate_session(session.id)
    assert validated is None

    reloaded_session = await session_service.repository.get_by_id(session.id)
    assert reloaded_session is not None
    assert reloaded_session.status == SessionStatus.REVOKED

    # Verify token_2 is also invalid now because family was revoked
    with pytest.raises((TokenReuseDetectedError, SessionRevokedError)):
        await session_service.rotate_refresh_token(token_2)


@pytest.mark.asyncio
async def test_refresh_token_rotation_fails_if_session_revoked(
    db_session: AsyncSession,
) -> None:
    """Rotating a refresh token whose session was manually revoked raises SessionRevokedError."""
    user = User(
        email="revoked@example.com",
        normalized_email="revoked@example.com",
        display_name="Revoked User",
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    await db_session.flush()

    session_service = SessionService(db_session)
    session, token = await session_service.create_session(user_id=user.id)
    await db_session.commit()

    # Manually revoke session
    await session_service.revoke_session(user.id, session.id)
    await db_session.commit()

    with pytest.raises(SessionRevokedError):
        await session_service.rotate_refresh_token(token)


@pytest.mark.asyncio
async def test_refresh_token_rotation_fails_if_expired(
    db_session: AsyncSession,
) -> None:
    """Rotating an expired refresh token raises InvalidRefreshTokenError."""
    user = User(
        email="expired@example.com",
        normalized_email="expired@example.com",
        display_name="Expired User",
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    await db_session.flush()

    session_service = SessionService(db_session)
    session, token = await session_service.create_session(user_id=user.id, ttl_seconds=-10)
    await db_session.commit()

    with pytest.raises(InvalidRefreshTokenError):
        await session_service.rotate_refresh_token(token)
