"""Repository for session and refresh token database operations (FCD-05 §9.2, §9.3)."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.session import (
    RefreshTokenRecord,
    SessionStatus,
    UserSession,
)
from menu_it.repositories.base import BaseRepository


class SessionRepository(BaseRepository[UserSession]):
    """Data access repository for UserSession and RefreshTokenRecord entities."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserSession)

    async def get_by_id(self, session_id: UUID) -> UserSession | None:
        """Fetch session by UUID primary key."""
        statement = select(UserSession).where(UserSession.id == session_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update_last_activity(self, session_id: UUID) -> None:
        """Touch last_activity_at timestamp."""
        statement = (
            update(UserSession)
            .where(UserSession.id == session_id)
            .values(last_activity_at=datetime.now(UTC))
        )
        await self.session.execute(statement)
        await self.session.flush()

    async def revoke_session(self, session_id: UUID) -> bool:
        """Revoke a single session by marking status REVOKED."""
        session = await self.get_by_id(session_id)
        if not session or session.status == SessionStatus.REVOKED:
            return False
        session.status = SessionStatus.REVOKED
        await self.session.flush()
        return True

    async def revoke_all_user_sessions(
        self,
        user_id: UUID,
        *,
        except_session_id: UUID | None = None,
    ) -> int:
        """Revoke all active sessions for a user, optionally excluding a specific session."""
        statement = update(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.status == SessionStatus.ACTIVE,
        )
        if except_session_id:
            statement = statement.where(UserSession.id != except_session_id)
        statement = statement.values(status=SessionStatus.REVOKED)
        result = await self.session.execute(statement)
        await self.session.flush()
        return int(result.rowcount)

    async def list_user_sessions(
        self,
        user_id: UUID,
        *,
        active_only: bool = True,
    ) -> list[UserSession]:
        """List sessions belonging to a user ordered by last activity descending."""
        statement = select(UserSession).where(UserSession.user_id == user_id)
        if active_only:
            statement = statement.where(UserSession.status == SessionStatus.ACTIVE)
        statement = statement.order_by(UserSession.last_activity_at.desc())
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    # --- Refresh Token Operations ---

    async def create_refresh_token(
        self,
        *,
        session_id: UUID,
        family_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshTokenRecord:
        """Persist a new hashed refresh token."""
        record = RefreshTokenRecord(
            session_id=session_id,
            family_id=family_id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=datetime.now(UTC),
            is_consumed=False,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_refresh_token_by_hash(
        self,
        token_hash: str,
        *,
        for_update: bool = False,
    ) -> RefreshTokenRecord | None:
        """Fetch refresh token record by SHA-256 hash, optionally locking the row."""
        statement = select(RefreshTokenRecord).where(RefreshTokenRecord.token_hash == token_hash)
        if for_update and self.session.bind and self.session.bind.dialect.name == "postgresql":
            # PostgreSQL supports FOR UPDATE row locking
            statement = statement.with_for_update()
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def mark_refresh_token_consumed(self, record_id: UUID) -> None:
        """Mark a refresh token as consumed during rotation."""
        statement = (
            update(RefreshTokenRecord)
            .where(RefreshTokenRecord.id == record_id)
            .values(is_consumed=True)
        )
        await self.session.execute(statement)
        await self.session.flush()

    async def revoke_token_family(self, family_id: UUID) -> int:
        """Revoke all tokens and the associated session for a token family upon reuse."""
        # Find session ID from family
        find_stmt = (
            select(RefreshTokenRecord.session_id)
            .where(RefreshTokenRecord.family_id == family_id)
            .limit(1)
        )
        res = await self.session.execute(find_stmt)
        session_id = res.scalar_one_or_none()
        if session_id:
            await self.revoke_session(session_id)

        # Delete or mark consumed all tokens in the family
        del_stmt = (
            update(RefreshTokenRecord)
            .where(RefreshTokenRecord.family_id == family_id)
            .values(is_consumed=True)
        )
        del_res = await self.session.execute(del_stmt)
        await self.session.flush()
        return int(del_res.rowcount)
