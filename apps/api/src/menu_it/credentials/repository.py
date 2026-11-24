"""Credential repository for user password persistence (FCD-05 §6.3)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.credential import UserCredential
from menu_it.repositories.base import BaseRepository


class CredentialRepository(BaseRepository[UserCredential]):
    """Data access repository for UserCredential entities."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserCredential)

    async def get_by_user_id(self, user_id: UUID) -> UserCredential | None:
        """Fetch credential record by user UUID."""
        statement = select(UserCredential).where(UserCredential.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def set_password_hash(self, user_id: UUID, password_hash: str) -> UserCredential:
        """Create or update password hash for user."""
        existing = await self.get_by_user_id(user_id)
        if existing:
            existing.password_hash = password_hash
            await self.session.flush()
            return existing

        new_cred = UserCredential(user_id=user_id, password_hash=password_hash)
        await self.create(new_cred)
        return new_cred
