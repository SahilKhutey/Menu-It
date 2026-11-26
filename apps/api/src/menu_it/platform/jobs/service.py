"""Job submission and lifecycle management service (FCD-10 WP-03)."""

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.background_job import BackgroundJobModel
from menu_it.platform.jobs.contracts import JobContext, JobEnvelope, JobStatus
from menu_it.platform.jobs.registry import is_valid_job_type

logger = logging.getLogger("menu_it.platform.jobs.service")


class JobService:
    """Service for submitting, tracking, and canceling background jobs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def submit_job(
        self,
        job_type: str,
        payload: dict,
        context: JobContext,
        idempotency_key: str | None = None,
        schema_version: int = 1,
    ) -> JobEnvelope:
        """Validate, persist, and enqueue a background job."""
        if not is_valid_job_type(job_type):
            raise ValueError(f"Job type '{job_type}' is not registered.")
        if not isinstance(payload, dict):
            raise ValueError("Job payload must be a dictionary.")

        now = datetime.now(UTC)
        job_id = uuid4()
        idem_key = idempotency_key or f"{job_type}:{job_id}"

        # If idempotency key provided, check for duplicate
        if idempotency_key:
            stmt = select(BackgroundJobModel).where(
                BackgroundJobModel.idempotency_key == idempotency_key
            )
            result = await self.session.execute(stmt)
            existing = result.scalars().first()
            if existing:
                return JobEnvelope(
                    job_id=existing.id,
                    job_type=existing.job_type,
                    schema_version=schema_version,
                    payload=existing.payload,
                    context=context,
                    created_at=existing.created_at,
                    idempotency_key=existing.idempotency_key or idem_key,
                )

        record = BackgroundJobModel(
            id=job_id,
            job_type=job_type,
            organization_id=context.organization_id,
            actor_user_id=context.actor_user_id,
            status=JobStatus.QUEUED.value,
            payload=payload,
            idempotency_key=idem_key,
            attempts=0,
            max_tries=5,
            created_at=now,
            updated_at=now,
        )
        self.session.add(record)
        await self.session.flush()

        envelope = JobEnvelope(
            job_id=job_id,
            job_type=job_type,
            schema_version=schema_version,
            payload=payload,
            context=context,
            created_at=now,
            idempotency_key=idem_key,
        )
        logger.info(f"Submitted background job: {job_id} ({job_type})")
        return envelope

    async def get_job(
        self,
        job_id: UUID,
        organization_id: UUID | None = None,
    ) -> BackgroundJobModel | None:
        """Retrieve job status by ID with optional tenant boundary."""
        stmt = select(BackgroundJobModel).where(BackgroundJobModel.id == job_id)
        if organization_id is not None:
            stmt = stmt.where(BackgroundJobModel.organization_id == organization_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def cancel_job(
        self,
        job_id: UUID,
        organization_id: UUID | None = None,
    ) -> bool:
        """Request job cancellation if still queued."""
        job = await self.get_job(job_id, organization_id)
        if not job or job.status != JobStatus.QUEUED.value:
            return False
        job.status = JobStatus.CANCELLED.value
        job.updated_at = datetime.now(UTC)
        await self.session.flush()
        return True
