"""
ModularMenu — Session Security Architecture (ARC-12 §4.3, ADR-0224).
Server-managed opaque sessions with idle/absolute expiration and revocation.
"""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4


@dataclass
class UserSession:
    """In-memory and persistence entity representing an active session."""

    id: UUID
    user_id: UUID
    session_hash: str
    created_at: datetime
    expires_at: datetime
    last_active_at: datetime
    is_revoked: bool = False

    def is_valid(self, now: datetime | None = None) -> bool:
        """Check if session is active, not revoked, and not expired."""
        if self.is_revoked:
            return False
        current_time = now or datetime.now(UTC)
        return current_time < self.expires_at


class SessionStore:
    """Authoritative server-side session registry."""

    def __init__(self) -> None:
        self._sessions: dict[str, UserSession] = {}

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """Calculate deterministic SHA-256 hash of opaque token."""
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    def create_session(
        self,
        user_id: UUID,
        max_age_seconds: int = 14 * 86400,
        idle_timeout_seconds: int = 86400,
    ) -> tuple[str, UserSession]:
        """Generate a cryptographically secure 256-bit token and persist session."""
        raw_token = secrets.token_hex(32)
        session_hash = self.hash_token(raw_token)
        now = datetime.now(UTC)

        session = UserSession(
            id=uuid4(),
            user_id=user_id,
            session_hash=session_hash,
            created_at=now,
            expires_at=now + timedelta(seconds=max_age_seconds),
            last_active_at=now,
            is_revoked=False,
        )
        self._sessions[session_hash] = session
        return raw_token, session

    def get_session(self, raw_token: str) -> UserSession | None:
        """Retrieve and validate session, checking expiration and idle timeout."""
        session_hash = self.hash_token(raw_token)
        session = self._sessions.get(session_hash)
        if not session or not session.is_valid():
            return None

        # Update last active timestamp
        session.last_active_at = datetime.now(UTC)
        return session

    def rotate_session(self, raw_token: str) -> tuple[str, UserSession] | None:
        """Rotate token upon privilege change, invalidating old token."""
        old_session = self.get_session(raw_token)
        if not old_session:
            return None

        # Revoke old session
        self.revoke_session(raw_token)

        # Create new session retaining original creation & remaining lifespan
        new_token, new_session = self.create_session(
            user_id=old_session.user_id,
            max_age_seconds=int((old_session.expires_at - datetime.now(UTC)).total_seconds()),
        )
        return new_token, new_session

    def revoke_session(self, raw_token: str) -> bool:
        """Explicitly revoke single session on logout."""
        session_hash = self.hash_token(raw_token)
        session = self._sessions.get(session_hash)
        if session:
            session.is_revoked = True
            return True
        return False

    def revoke_all_user_sessions(self, user_id: UUID) -> int:
        """Revoke all sessions for user upon password reset or account suspension."""
        count = 0
        for session in self._sessions.values():
            if session.user_id == user_id and not session.is_revoked:
                session.is_revoked = True
                count += 1
        return count


session_store = SessionStore()
