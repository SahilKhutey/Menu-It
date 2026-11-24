"""Integration tests for email verification workflow (FCD-05 §10)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.user import User, UserStatus
from menu_it.verification.exceptions import InvalidVerificationTokenError
from menu_it.verification.service import EmailVerificationService


@pytest.mark.asyncio
async def test_email_verification_success(db_session: AsyncSession) -> None:
    """Valid token sets email_verified=True and transitions status from PENDING to ACTIVE."""
    user = User(
        email="verify_test@example.com",
        normalized_email="verify_test@example.com",
        display_name="Verify Candidate",
        status=UserStatus.PENDING_VERIFICATION,
        email_verified=False,
    )
    db_session.add(user)
    await db_session.flush()

    service = EmailVerificationService(db_session)
    raw_token = await service.create_verification_token(user.id)
    await db_session.commit()

    # Verify email
    verified_user = await service.verify_email(raw_token)
    await db_session.commit()

    assert verified_user.id == user.id
    assert verified_user.email_verified is True
    assert verified_user.status == UserStatus.ACTIVE


@pytest.mark.asyncio
async def test_email_verification_consumed_token_fails(db_session: AsyncSession) -> None:
    """A verification token cannot be consumed more than once."""
    user = User(
        email="verify_reuse@example.com",
        normalized_email="verify_reuse@example.com",
        display_name="Verify Reuse",
        status=UserStatus.PENDING_VERIFICATION,
        email_verified=False,
    )
    db_session.add(user)
    await db_session.flush()

    service = EmailVerificationService(db_session)
    raw_token = await service.create_verification_token(user.id)
    await db_session.commit()

    await service.verify_email(raw_token)
    await db_session.commit()

    with pytest.raises(InvalidVerificationTokenError) as exc:
        await service.verify_email(raw_token)
    assert "already been used" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_email_verification_expired_token_fails(db_session: AsyncSession) -> None:
    """Expired verification token is rejected."""
    user = User(
        email="verify_expired@example.com",
        normalized_email="verify_expired@example.com",
        display_name="Verify Expired",
        status=UserStatus.PENDING_VERIFICATION,
        email_verified=False,
    )
    db_session.add(user)
    await db_session.flush()

    service = EmailVerificationService(db_session)
    raw_token = await service.create_verification_token(user.id, ttl_seconds=-10)
    await db_session.commit()

    with pytest.raises(InvalidVerificationTokenError) as exc:
        await service.verify_email(raw_token)
    assert "expired" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_resend_verification_lifecycle(db_session: AsyncSession) -> None:
    """Resend produces a token for unverified accounts, but returns None for verified accounts."""
    user = User(
        email="resend_test@example.com",
        normalized_email="resend_test@example.com",
        display_name="Resend Candidate",
        status=UserStatus.PENDING_VERIFICATION,
        email_verified=False,
    )
    db_session.add(user)
    await db_session.commit()

    service = EmailVerificationService(db_session)

    # 1. Unverified -> returns fresh token
    token = await service.resend_verification("resend_test@example.com")
    assert token is not None

    # 2. Unknown email -> returns None
    assert await service.resend_verification("unknown@example.com") is None

    # 3. Mark verified -> returns None
    await service.verify_email(token)
    await db_session.commit()
    assert await service.resend_verification("resend_test@example.com") is None
