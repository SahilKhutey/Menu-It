"""Email verification service managing token generation and account activation (FCD-05 §10)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.tokens import (
    generate_opaque_token,
    hash_opaque_token,
)
from menu_it.database.models.user import User, UserStatus, normalize_email
from menu_it.database.models.verification import EmailVerificationToken
from menu_it.verification.exceptions import InvalidVerificationTokenError


class EmailVerificationService:
    """Service handling email verification tokens and state transitions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_verification_token(
        self,
        user_id: UUID,
        *,
        ttl_seconds: int = 86400,
    ) -> str:
        """Issue an email verification token, returning the raw token string for delivery."""
        raw_token = generate_opaque_token()
        token_hash = hash_opaque_token(raw_token)
        now = datetime.now(UTC)

        token_record = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=now + timedelta(seconds=ttl_seconds),
            created_at=now,
        )
        self.session.add(token_record)
        await self.session.flush()
        return raw_token

    async def verify_email(self, raw_token: str) -> User:
        """Validate token and activate user account."""
        token_hash = hash_opaque_token(raw_token)
        now = datetime.now(UTC)

        statement = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash
        )
        result = await self.session.execute(statement)
        token_record = result.scalar_one_or_none()

        if not token_record or token_record.consumed_at is not None:
            raise InvalidVerificationTokenError(
                "Verification token is invalid or has already been used."
            )

        exp = token_record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)

        if exp < now:
            raise InvalidVerificationTokenError("Verification token has expired.")

        # Consume token
        token_record.consumed_at = now

        # Fetch and activate user
        user = await self.session.get(User, token_record.user_id)
        if not user:
            raise InvalidVerificationTokenError("Associated user does not exist.")

        user.email_verified = True
        if user.status == UserStatus.PENDING_VERIFICATION:
            user.status = UserStatus.ACTIVE

        await self.session.flush()
        return user

    async def resend_verification(self, email: str, *, ttl_seconds: int = 86400) -> str | None:
        """Generate fresh verification token if user exists and is unverified."""
        norm = normalize_email(email)
        statement = select(User).where(User.normalized_email == norm)
        result = await self.session.execute(statement)
        user = result.scalar_one_or_none()

        if not user or user.email_verified:
            return None

        return await self.create_verification_token(user.id, ttl_seconds=ttl_seconds)
