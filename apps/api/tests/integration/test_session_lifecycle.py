"""Integration tests for session lifecycle, expiration, and revocation (FCD-05 §9, §21.5)."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.session import SessionStatus
from menu_it.database.models.user import User, UserStatus
from menu_it.sessions.exceptions import SessionNotFoundError
from menu_it.sessions.service import SessionService


@pytest.mark.asyncio
async def test_session_lifecycle_and_validation(db_session: AsyncSession):
    """Verify session creation, validation, and single session revocation."""
    session_svc = SessionService(db_session)
    user = User(
        id=uuid4(),
        email="sess_user@example.com",
        normalized_email="sess_user@example.com",
        display_name="Session User",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    # 1. Create session
    sess, raw_refresh = await session_svc.create_session(
        user_id=user.id,
        ip_address="10.0.0.1",
        user_agent="TestAgent",
    )
    await db_session.commit()

    # 2. Validate active session
    valid = await session_svc.validate_session(sess.id)
    assert valid is not None
    assert valid.status == SessionStatus.ACTIVE

    # 3. Revoke session
    revoked = await session_svc.revoke_session(user.id, sess.id)
    await db_session.commit()
    assert revoked is True

    # 4. Validating revoked session returns None
    assert await session_svc.validate_session(sess.id) is None


@pytest.mark.asyncio
async def test_session_expiry(db_session: AsyncSession):
    """Verify expired session is detected and rejected."""
    session_svc = SessionService(db_session)
    user = User(
        id=uuid4(),
        email="exp_user@example.com",
        normalized_email="exp_user@example.com",
        display_name="Exp User",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Create session with negative TTL
    sess, _ = await session_svc.create_session(
        user_id=user.id,
        ttl_seconds=-10,
    )
    await db_session.commit()

    assert await session_svc.validate_session(sess.id) is None


@pytest.mark.asyncio
async def test_revoke_all_user_sessions(db_session: AsyncSession):
    """Verify logout-all revokes all sessions belonging to user."""
    session_svc = SessionService(db_session)
    user = User(
        id=uuid4(),
        email="multi_sess@example.com",
        normalized_email="multi_sess@example.com",
        display_name="Multi User",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    s1, _ = await session_svc.create_session(user_id=user.id)
    s2, _ = await session_svc.create_session(user_id=user.id)
    s3, _ = await session_svc.create_session(user_id=user.id)
    await db_session.commit()

    # Revoke all except s3 (e.g. current device session)
    count = await session_svc.revoke_all_user_sessions(user.id, except_session_id=s3.id)
    await db_session.commit()
    assert count == 2

    assert await session_svc.validate_session(s1.id) is None
    assert await session_svc.validate_session(s2.id) is None
    assert await session_svc.validate_session(s3.id) is not None


@pytest.mark.asyncio
async def test_revoke_another_users_session_rejected(db_session: AsyncSession):
    """Verify user cannot revoke another user's session."""
    session_svc = SessionService(db_session)
    user_a = User(
        id=uuid4(),
        email="ua@example.com",
        normalized_email="ua@example.com",
        display_name="User A",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    user_b = User(
        id=uuid4(),
        email="ub@example.com",
        normalized_email="ub@example.com",
        display_name="User B",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add_all([user_a, user_b])
    await db_session.commit()

    sess_b, _ = await session_svc.create_session(user_id=user_b.id)
    await db_session.commit()

    with pytest.raises(SessionNotFoundError):
        await session_svc.revoke_session(user_a.id, sess_b.id)
