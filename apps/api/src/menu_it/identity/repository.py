"""Repository for user identity persistence operations (FCD-05 §5.1)."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.user import User, UserStatus, normalize_email
from menu_it.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access repository for User entities."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_normalized_email(self, email: str) -> User | None:
        """Fetch user by normalized email address."""
        norm = normalize_email(email)
        statement = select(User).where(User.normalized_email == norm)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered."""
        norm = normalize_email(email)
        statement = select(User.id).where(User.normalized_email == norm)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() is not None

    async def record_failed_login(
        self,
        user: User,
        *,
        max_attempts: int = 5,
        lockout_seconds: int = 900,
    ) -> bool:
        """Increment failed attempts and lock account if max attempts reached.

        Returns True if the account became locked as a result.
        """
        user.failed_login_attempts += 1
        is_now_locked = False
        if user.failed_login_attempts >= max_attempts:
            user.status = UserStatus.LOCKED
            user.locked_until = datetime.now(UTC) + timedelta(seconds=lockout_seconds)
            is_now_locked = True
        await self.session.flush()
        return is_now_locked

    async def reset_failed_logins(self, user: User) -> None:
        """Clear failed login attempts counter and unlock timestamp."""
        user.failed_login_attempts = 0
        user.locked_until = None
        if user.status == UserStatus.LOCKED:
            user.status = UserStatus.ACTIVE
        await self.session.flush()
