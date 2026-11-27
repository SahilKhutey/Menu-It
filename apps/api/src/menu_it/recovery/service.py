"""Password recovery service managing reset tokens and atomic credential updates (FCD-05 §11)."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.tokens import (
    generate_opaque_token,
    hash_opaque_token,
)
from menu_it.credentials.hashing import hash_password
from menu_it.credentials.password_policy import validate_password
from menu_it.credentials.repository import CredentialRepository
from menu_it.database.models.recovery import PasswordResetToken
from menu_it.database.models.user import User, UserStatus, normalize_email
from menu_it.recovery.exceptions import InvalidRecoveryTokenError
from menu_it.sessions.repository import SessionRepository


class PasswordRecoveryService:
    """Service handling password recovery tokens, credential resets, and session invalidation."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.credentials = CredentialRepository(session)
        self.sessions = SessionRepository(session)

    async def create_password_reset_token(
        self,
        email: str,
        *,
        ttl_seconds: int = 1800,  # 30 minutes
    ) -> str | None:
        """Issue a password reset token if user exists and is in good standing.

        Returns the raw token string for delivery, or None if user not eligible.
        """
        norm = normalize_email(email)
        statement = select(User).where(User.normalized_email == norm)
        result = await self.session.execute(statement)
        user = result.scalar_one_or_none()

        if not user or user.status not in (UserStatus.ACTIVE, UserStatus.LOCKED):
            return None

        raw_token = generate_opaque_token()
        token_hash = hash_opaque_token(raw_token)
        now = datetime.now(UTC)

        token_record = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now + timedelta(seconds=ttl_seconds),
            created_at=now,
        )
        self.session.add(token_record)
        await self.session.flush()
        return raw_token

    async def reset_password(
        self,
        raw_token: str,
        new_password: str,
    ) -> User:
        """Validate token, update password hash, and revoke all existing sessions."""
        validate_password(new_password)

        token_hash = hash_opaque_token(raw_token)
        now = datetime.now(UTC)

        statement = select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        result = await self.session.execute(statement)
        token_record = result.scalar_one_or_none()

        if not token_record or token_record.consumed_at is not None:
            raise InvalidRecoveryTokenError(
                "Password reset token is invalid or has already been used."
            )

        exp = token_record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)

        if exp < now:
            raise InvalidRecoveryTokenError("Password reset token has expired.")

        # Consume token
        token_record.consumed_at = now

        user = await self.session.get(User, token_record.user_id)
        if not user or user.status in (UserStatus.SUSPENDED, UserStatus.DEACTIVATED):
            raise InvalidRecoveryTokenError("User account is inactive or not found.")

        # Update password hash
        new_hash = hash_password(new_password)
        await self.credentials.set_password_hash(user.id, new_hash)

        # Unlock account if locked
        if user.status == UserStatus.LOCKED:
            user.status = UserStatus.ACTIVE
            user.failed_login_attempts = 0
            user.locked_until = None

        # Revoke ALL existing active user sessions across all devices (FCD-05 §11.2)
        await self.sessions.revoke_all_user_sessions(user.id)

        await self.session.flush()
        return user
