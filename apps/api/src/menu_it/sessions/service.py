"""Session management service for lifecycle, rotation, and reuse detection (FCD-05 §9.3)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.tokens import (
    generate_refresh_token,
    hash_refresh_token,
)
from menu_it.database.models.session import (
    SessionStatus,
    UserSession,
)
from menu_it.sessions.exceptions import (
    InvalidRefreshTokenError,
    SessionNotFoundError,
    SessionRevokedError,
    TokenReuseDetectedError,
)
from menu_it.sessions.repository import SessionRepository


class SessionService:
    """Service coordinating session lifecycle and cryptographic refresh token rotation."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SessionRepository(session)

    async def create_session(
        self,
        *,
        user_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
        ttl_seconds: int = 2592000,  # 30 days
    ) -> tuple[UserSession, str]:
        """Create a new authenticated session and issue initial opaque refresh token."""
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=ttl_seconds)

        user_session = UserSession(
            user_id=user_id,
            status=SessionStatus.ACTIVE,
            ip_address=ip_address,
            user_agent=user_agent,
            last_activity_at=now,
            expires_at=expires_at,
        )
        await self.repository.create(user_session)

        # Issue initial refresh token in a fresh token family
        raw_refresh_token = generate_refresh_token()
        token_hash = hash_refresh_token(raw_refresh_token)
        family_id = uuid4()

        await self.repository.create_refresh_token(
            session_id=user_session.id,
            family_id=family_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        return user_session, raw_refresh_token

    async def validate_session(self, session_id: UUID) -> UserSession | None:
        """Validate session exists, is ACTIVE, and has not expired."""
        user_session = await self.repository.get_by_id(session_id)
        if not user_session:
            return None

        now = datetime.now(UTC)
        if user_session.status != SessionStatus.ACTIVE:
            return None

        # Compare timezone-aware datetimes
        exp = user_session.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)

        if exp < now:
            user_session.status = SessionStatus.EXPIRED
            await self.session.flush()
            return None

        await self.repository.update_last_activity(session_id)
        return user_session

    async def rotate_refresh_token(
        self,
        raw_refresh_token: str,
        *,
        ttl_seconds: int = 2592000,
    ) -> tuple[UserSession, str]:
        """Atomically rotate refresh token with strict reuse detection and family revocation.

        Security Invariants (FCD-05 §8.4):
        1. Token hash looked up with row locking (SELECT ... FOR UPDATE).
        2. If token record was already consumed -> REUSE DETECTED! Revoke family and session.
        3. Consume previous token and issue new token in the same family.
        """
        token_hash = hash_refresh_token(raw_refresh_token)
        record = await self.repository.get_refresh_token_by_hash(
            token_hash,
            for_update=True,
        )

        if not record:
            raise InvalidRefreshTokenError("Refresh token not found or invalid.")

        now = datetime.now(UTC)

        # 1. Reuse Detection
        if record.is_consumed:
            await self.repository.revoke_token_family(record.family_id)
            raise TokenReuseDetectedError(
                "Refresh token reuse detected. Token family and session have been revoked."
            )

        # 2. Expiry check
        exp = record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)

        if exp < now:
            raise InvalidRefreshTokenError("Refresh token has expired.")

        # 3. Session status check
        user_session = await self.repository.get_by_id(record.session_id)
        if not user_session or user_session.status != SessionStatus.ACTIVE:
            raise SessionRevokedError("Associated session is no longer active.")

        sess_exp = user_session.expires_at
        if sess_exp.tzinfo is None:
            sess_exp = sess_exp.replace(tzinfo=UTC)

        if sess_exp < now:
            user_session.status = SessionStatus.EXPIRED
            await self.session.flush()
            raise InvalidRefreshTokenError("Associated session has expired.")

        # 4. Consume current token
        await self.repository.mark_refresh_token_consumed(record.id)

        # 5. Issue new refresh token in the same token family
        new_raw_token = generate_refresh_token()
        new_token_hash = hash_refresh_token(new_raw_token)
        new_expires_at = now + timedelta(seconds=ttl_seconds)

        await self.repository.create_refresh_token(
            session_id=user_session.id,
            family_id=record.family_id,
            token_hash=new_token_hash,
            expires_at=new_expires_at,
        )

        # 6. Update session activity and extend expiry
        user_session.last_activity_at = now
        user_session.expires_at = new_expires_at
        await self.session.flush()

        return user_session, new_raw_token

    async def revoke_session(self, user_id: UUID, session_id: UUID) -> bool:
        """Revoke a single session, verifying user ownership."""
        user_session = await self.repository.get_by_id(session_id)
        if not user_session or user_session.user_id != user_id:
            raise SessionNotFoundError("Session not found.")
        return await self.repository.revoke_session(session_id)

    async def revoke_all_user_sessions(
        self,
        user_id: UUID,
        *,
        except_session_id: UUID | None = None,
    ) -> int:
        """Revoke all active sessions for a user, optionally retaining current session."""
        return await self.repository.revoke_all_user_sessions(
            user_id,
            except_session_id=except_session_id,
        )

    async def list_user_sessions(self, user_id: UUID) -> list[UserSession]:
        """List all active sessions for a user."""
        return await self.repository.list_user_sessions(user_id, active_only=True)
