"""Dead-letter queue persistence, inspection, and replay service (FCD-10 WP-04)."""

from datetime import datetime, timezone
import logging
from uuid import UUID, uuid4

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.dead_letter_job import DeadLetterJobModel
from menu_it.platform.jobs.contracts import JobContext, JobEnvelope

logger = logging.getLogger("menu_it.platform.jobs.dead_letter")


class DeadLetterService:
    """Service for recording, querying, and replaying dead-lettered background jobs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record_dead_letter(
        self,
        job_id: UUID,
        job_type: str,
        payload: dict,
        failure_code: str,
        failure_message: str,
        attempts: int,
        correlation_id: str,
        organization_id: UUID | None = None,
        first_failed_at: datetime | None = None,
    ) -> DeadLetterJobModel:
        """Persist a failed job record into the dead_letter_jobs table."""
        now = datetime.now(timezone.utc)
        record = DeadLetterJobModel(
            id=uuid4(),
            job_id=job_id,
            organization_id=organization_id,
            job_type=job_type,
            payload=payload,
            failure_code=failure_code,
            failure_message=failure_message,
            attempts=attempts,
            first_failed_at=first_failed_at or now,
            dead_lettered_at=now,
            correlation_id=correlation_id,
        )
        self.session.add(record)
        await self.session.flush()
        logger.warning(
            f"Job {job_id} ({job_type}) dead-lettered after {attempts} attempts: {failure_code} - {failure_message}"
        )
        return record

    async def list_dead_letters(
        self,
        organization_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DeadLetterJobModel]:
        """List dead letters with tenant scoping."""
        query = select(DeadLetterJobModel).order_by(desc(DeadLetterJobModel.dead_lettered_at))
        if organization_id is not None:
            query = query.where(DeadLetterJobModel.organization_id == organization_id)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_dead_letter(
        self,
        record_id: UUID,
        organization_id: UUID | None = None,
    ) -> DeadLetterJobModel | None:
        """Retrieve a specific dead letter record."""
        query = select(DeadLetterJobModel).where(DeadLetterJobModel.id == record_id)
        if organization_id is not None:
            query = query.where(DeadLetterJobModel.organization_id == organization_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def mark_replayed(
        self,
        record_id: UUID,
        replayed_by: UUID,
        organization_id: UUID | None = None,
    ) -> DeadLetterJobModel | None:
        """Mark dead letter as replayed with attribution."""
        record = await self.get_dead_letter(record_id, organization_id)
        if not record:
            return None
        record.replayed_at = datetime.now(timezone.utc)
        record.replayed_by = replayed_by
        await self.session.flush()
        return record
