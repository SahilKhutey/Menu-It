"""Authentication service orchestrating registration, login, and token issuance (FCD-05 §7)."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.exceptions import (
    AccountLockedError,
    AccountNotActiveError,
    AccountSuspendedError,
    InvalidCredentialsError,
)
from menu_it.authentication.tokens import (
    create_access_token,
)
from menu_it.core.config import get_settings
from menu_it.credentials.hashing import (
    hash_password,
    needs_rehash,
    perform_dummy_verification,
    verify_password,
)
from menu_it.credentials.password_policy import validate_password
from menu_it.credentials.repository import CredentialRepository
from menu_it.database.models.credential import UserCredential
from menu_it.database.models.session import UserSession
from menu_it.database.models.user import User, UserStatus, normalize_email
from menu_it.identity.exceptions import UserAlreadyExistsError
from menu_it.identity.repository import UserRepository
from menu_it.sessions.service import SessionService
from menu_it.verification.service import EmailVerificationService


class AuthenticationService:
    """Core service managing user authentication, sessions, and token issuance."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.credentials = CredentialRepository(session)
        self.sessions = SessionService(session)
        self.verification = EmailVerificationService(session)
        self.settings = get_settings()

    async def register(
        self,
        *,
        email: str,
        display_name: str,
        password: str,
    ) -> tuple[User, str]:
        """Self-service registration creating pending user, credential, and verification token."""
        validate_password(password)
        normalized = normalize_email(email)

        if await self.users.email_exists(normalized):
            raise UserAlreadyExistsError(f"An account with the email '{email}' already exists.")

        user = User(
            email=email.strip(),
            normalized_email=normalized,
            display_name=display_name.strip(),
            email_verified=False,
            status=UserStatus.PENDING_VERIFICATION,
        )
        await self.users.create(user)

        # Store password hash securely isolated in credentials table
        hashed = hash_password(password)
        await self.credentials.set_password_hash(user.id, hashed)

        # Issue initial email verification token
        verification_token = await self.verification.create_verification_token(
            user.id,
            ttl_seconds=self.settings.auth_email_verification_ttl_seconds,
        )

        return user, verification_token

    async def login(
        self,
        *,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, UserSession, str, str]:
        """Authenticate user credentials and issue access + refresh tokens.

        Security Safeguards:
        1. Timing attack mitigation via dummy work if user doesn't exist.
        2. Account lockout tracking on repeated failures.
        3. Transparent password hash parameter upgrades.
        4. Atomic session and refresh-token family generation.
        """
        normalized = normalize_email(email)

        statement = (
            select(User, UserCredential)
            .join(UserCredential, UserCredential.user_id == User.id)
            .where(User.normalized_email == normalized)
        )
        result = await self.session.execute(statement)
        row = result.first()

        if not row:
            perform_dummy_verification(password)
            raise InvalidCredentialsError("Invalid email or password.")

        user, cred = row

        # Check existing lockout state
        now = datetime.now(UTC)
        if user.status == UserStatus.LOCKED:
            if user.locked_until:
                locked_until = user.locked_until
                if locked_until.tzinfo is None:
                    locked_until = locked_until.replace(tzinfo=UTC)

                if locked_until > now:
                    raise AccountLockedError(
                        "Account is temporarily locked due to excessive failed attempts. "
                        "Please try again later."
                    )
            # Lockout expired, restore to active
            await self.users.reset_failed_logins(user)

        # Verify password against Argon2id hash
        if not verify_password(cred.password_hash, password):
            is_locked = await self.users.record_failed_login(
                user,
                max_attempts=self.settings.auth_max_failed_logins,
                lockout_seconds=self.settings.auth_lockout_seconds,
            )
            if is_locked:
                raise AccountLockedError(
                    "Account has been temporarily locked due to excessive failed attempts."
                )
            raise InvalidCredentialsError("Invalid email or password.")

        # Validate account status
        if user.status == UserStatus.SUSPENDED:
            raise AccountSuspendedError("Account has been suspended.")
        if user.status == UserStatus.DEACTIVATED:
            raise AccountNotActiveError("Account is deactivated.")

        # Reset failed attempts counter upon successful verification
        await self.users.reset_failed_logins(user)

        # Upgrade password hash if Argon2 parameters have been updated
        if needs_rehash(cred.password_hash):
            new_hash = hash_password(password)
            cred.password_hash = new_hash
            await self.session.flush()

        # Create session and initial refresh token
        user_session, raw_refresh_token = await self.sessions.create_session(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            ttl_seconds=self.settings.auth_refresh_token_ttl_seconds,
        )

        # Issue access JWT
        access_token = create_access_token(
            user_id=user.id,
            session_id=user_session.id,
            signing_key=self.settings.auth_secret_key,
            algorithm=self.settings.auth_jwt_algorithm,
            key_id=self.settings.auth_key_id,
            issuer=self.settings.auth_issuer,
            audience=self.settings.auth_audience,
            ttl_seconds=self.settings.auth_access_token_ttl_seconds,
        )

        return user, user_session, access_token, raw_refresh_token

    async def refresh_tokens(
        self,
        raw_refresh_token: str,
    ) -> tuple[UserSession, str, str]:
        """Rotate refresh token and issue a fresh access token."""
        user_session, new_raw_refresh = await self.sessions.rotate_refresh_token(
            raw_refresh_token,
            ttl_seconds=self.settings.auth_refresh_token_ttl_seconds,
        )

        access_token = create_access_token(
            user_id=user_session.user_id,
            session_id=user_session.id,
            signing_key=self.settings.auth_secret_key,
            algorithm=self.settings.auth_jwt_algorithm,
            key_id=self.settings.auth_key_id,
            issuer=self.settings.auth_issuer,
            audience=self.settings.auth_audience,
            ttl_seconds=self.settings.auth_access_token_ttl_seconds,
        )

        return user_session, access_token, new_raw_refresh

    async def change_password(
        self,
        *,
        user_id: UUID,
        current_password: str,
        new_password: str,
        current_session_id: UUID | None = None,
    ) -> None:
        """Authenticated password change verifying current password and revoking other sessions."""
        validate_password(new_password)

        cred = await self.credentials.get_by_user_id(user_id)
        if not cred or not verify_password(cred.password_hash, current_password):
            raise InvalidCredentialsError("Current password is not correct.")

        new_hash = hash_password(new_password)
        await self.credentials.set_password_hash(user_id, new_hash)

        # Revoke all other active sessions (retaining current device session)
        await self.sessions.revoke_all_user_sessions(
            user_id,
            except_session_id=current_session_id,
        )
