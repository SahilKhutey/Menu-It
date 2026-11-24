"""Security tests for authentication controls and attack mitigations (FCD-05 §14, §17)."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.exceptions import AccountLockedError, InvalidCredentialsError
from menu_it.authentication.service import AuthenticationService
from menu_it.authentication.tokens import create_access_token
from menu_it.core.config import get_settings
from menu_it.credentials.hashing import hash_password
from menu_it.credentials.repository import CredentialRepository
from menu_it.database.models.user import User, UserStatus
from menu_it.security.rate_limiting import InMemoryRateLimiter


@pytest.mark.asyncio
async def test_tampered_jwt_signature_rejected(authed_client) -> None:
    """Tampering with JWT token signature or payload causes immediate 401 rejection."""
    settings = get_settings()
    user_id = uuid4()
    session_id = uuid4()

    valid_token = create_access_token(
        user_id=user_id,
        session_id=session_id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=900,
    )

    # Tamper with token by flipping signature characters
    tampered_token = valid_token[:-4] + ("ABCD" if not valid_token.endswith("ABCD") else "WXYZ")

    response = authed_client.get(
        "/api/v1/identity/me",
        headers={"Authorization": f"Bearer {tampered_token}"},
    )
    assert response.status_code == 401
    assert "invalid" in response.text.lower()


@pytest.mark.asyncio
async def test_expired_jwt_rejected(authed_client) -> None:
    """Expired JWT token is rejected with 401 error."""
    settings = get_settings()
    user_id = uuid4()
    session_id = uuid4()

    expired_token = create_access_token(
        user_id=user_id,
        session_id=session_id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=-30,  # Already expired
    )

    response = authed_client.get(
        "/api/v1/identity/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert "expired" in response.text.lower()


@pytest.mark.asyncio
async def test_invalid_audience_or_issuer_rejected(authed_client) -> None:
    """JWT issued for a different audience or by an untrusted issuer is rejected."""
    settings = get_settings()
    user_id = uuid4()
    session_id = uuid4()

    bad_issuer_token = create_access_token(
        user_id=user_id,
        session_id=session_id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer="https://untrusted-issuer.example.com",
        audience=settings.auth_audience,
        ttl_seconds=900,
    )

    response = authed_client.get(
        "/api/v1/identity/me",
        headers={"Authorization": f"Bearer {bad_issuer_token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_account_lockout_after_max_failed_attempts(db_session: AsyncSession) -> None:
    """Repeated failed login attempts trigger account lockout (FCD-05 §7.2, §14.2)."""
    user = User(
        email="bruteforce@example.com",
        normalized_email="bruteforce@example.com",
        display_name="Brute Force Target",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    cred_repo = CredentialRepository(db_session)
    await cred_repo.set_password_hash(user.id, hash_password("CorrectPassword123!"))
    await db_session.commit()

    auth_service = AuthenticationService(db_session)

    # First 4 attempts fail with InvalidCredentialsError
    for _ in range(4):
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login(
                email="bruteforce@example.com",
                password="WrongPassword999!",
            )

    # 5th attempt hits max_failed_logins and triggers AccountLockedError
    with pytest.raises(AccountLockedError):
        await auth_service.login(
            email="bruteforce@example.com",
            password="WrongPassword999!",
        )

    # Subsequent attempt fails while account is locked, even with correct password
    with pytest.raises(AccountLockedError):
        await auth_service.login(
            email="bruteforce@example.com",
            password="CorrectPassword123!",
        )


@pytest.mark.asyncio
async def test_rate_limiter_brute_force_mitigation() -> None:
    """Rate limiter restricts excessive requests per IP within the time window."""
    limiter = InMemoryRateLimiter()
    key = "192.168.1.100"

    # First 5 calls pass
    for _ in range(5):
        assert limiter.check_rate_limit(key, max_attempts=5, window_seconds=60) is True

    # 6th call is blocked
    assert limiter.check_rate_limit(key, max_attempts=5, window_seconds=60) is False
