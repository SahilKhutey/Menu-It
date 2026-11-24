"""Integration tests for registration workflow and user persistence (FCD-05 §7, §21.4)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.service import AuthenticationService
from menu_it.credentials.hashing import verify_password
from menu_it.credentials.repository import CredentialRepository
from menu_it.database.models.user import UserStatus
from menu_it.identity.exceptions import UserAlreadyExistsError


@pytest.mark.asyncio
async def test_registration_creates_pending_user_and_credential(db_session: AsyncSession):
    """Verify registration creates pending user, hashed credential, and verification token."""
    service = AuthenticationService(db_session)
    password = "A-long-and-unique-password-2026"

    user, verification_token = await service.register(
        email="newuser@example.com",
        display_name="New User",
        password=password,
    )
    await db_session.commit()

    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.normalized_email == "newuser@example.com"
    assert user.status == UserStatus.PENDING_VERIFICATION
    assert user.email_verified is False
    assert len(verification_token) >= 32

    # Verify credential was created with Argon2id hash
    cred_repo = CredentialRepository(db_session)
    cred = await cred_repo.get_by_user_id(user.id)
    assert cred is not None
    assert verify_password(cred.password_hash, password) is True


@pytest.mark.asyncio
async def test_duplicate_email_registration_rejected(db_session: AsyncSession):
    """Verify registration with already registered email raises UserAlreadyExistsError."""
    service = AuthenticationService(db_session)
    password = "A-long-and-unique-password-2026"

    await service.register(
        email="existing@example.com",
        display_name="Existing User",
        password=password,
    )
    await db_session.commit()

    with pytest.raises(UserAlreadyExistsError, match="already exists"):
        await service.register(
            email="EXISTING@example.com",
            display_name="Duplicate Attempt",
            password=password,
        )


@pytest.mark.asyncio
async def test_invalid_password_registration_rejected(db_session: AsyncSession):
    """Verify registration with weak password raises ValueError."""
    service = AuthenticationService(db_session)

    with pytest.raises(ValueError, match="at least 12 characters"):
        await service.register(
            email="user2@example.com",
            display_name="User Two",
            password="short",
        )
