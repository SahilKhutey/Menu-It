"""Idempotency service and hashing logic (FCD-07 WP-11)."""

import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.idempotency import IdempotencyRecord


class IdempotencyService:
    """Manages idempotency record lifecycle, payload hashing, and replay validation."""

    DEFAULT_TTL_SECONDS: int = 86400  # 24 hours

    @staticmethod
    def compute_payload_hash(method: str, path: str, body: bytes) -> str:
        """Compute SHA-256 hash of HTTP method, path, and request body payload."""
        hasher = hashlib.sha256()
        hasher.update(method.upper().encode("utf-8"))
        hasher.update(b":")
        hasher.update(path.encode("utf-8"))
        hasher.update(b":")
        hasher.update(body)
        return hasher.hexdigest()

    @classmethod
    async def get_record(
        cls,
        session: AsyncSession,
        organization_id: UUID,
        actor_id: UUID | None,
        key: str,
    ) -> IdempotencyRecord | None:
        """Find non-expired idempotency record for given tenant and actor."""
        stmt = select(IdempotencyRecord).where(
            IdempotencyRecord.organization_id == organization_id,
            IdempotencyRecord.key == key,
        )
        if actor_id is not None:
            stmt = stmt.where(IdempotencyRecord.actor_id == actor_id)
        else:
            stmt = stmt.where(IdempotencyRecord.actor_id.is_(None))

        result = await session.execute(stmt)
        record = result.scalar_one_or_none()

        if record is None:
            return None

        # Check expiration
        now = datetime.now(UTC)
        expires_at = record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)

        if expires_at <= now:
            # Expired: purge it
            await session.delete(record)
            await session.commit()
            return None

        return record

    @classmethod
    async def save_record(
        cls,
        session: AsyncSession,
        organization_id: UUID,
        actor_id: UUID | None,
        key: str,
        request_hash: str,
        response_status: int,
        response_body: Any,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> IdempotencyRecord:
        """Persist a response for an idempotent key."""
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=ttl_seconds)

        record = IdempotencyRecord(
            organization_id=organization_id,
            actor_id=actor_id,
            key=key,
            request_hash=request_hash,
            response_status=response_status,
            response_body=response_body,
            created_at=now,
            expires_at=expires_at,
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record

    @classmethod
    async def purge_expired(cls, session: AsyncSession) -> int:
        """Purge all expired idempotency records."""
        now = datetime.now(UTC)
        stmt = delete(IdempotencyRecord).where(IdempotencyRecord.expires_at <= now)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount
