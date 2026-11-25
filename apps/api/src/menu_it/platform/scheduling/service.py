"""Scheduling management service (FCD-10 WP-07)."""

from datetime import datetime, timezone
import logging
from uuid import UUID, uuid4

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.scheduled_job import (
    ScheduledJobModel,
    ScheduledJobRunModel,
)
from menu_it.platform.scheduling.recurrence import compute_next_run_at

logger = logging.getLogger("menu_it.platform.scheduling.service")


class SchedulingService:
    """Service for managing persistent schedule definitions and execution history."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_schedule(
        self,
        job_type: str,
        payload: dict,
        schedule_type: str,
        schedule_expression: str | None = None,
        tz_name: str = "UTC",
        organization_id: UUID | None = None,
    ) -> ScheduledJobModel:
        """Define and persist a new scheduled job."""
        now = datetime.now(timezone.utc)
        next_run = compute_next_run_at(
            schedule_type=schedule_type,
            expression=schedule_expression,
            tz_name=tz_name,
            from_time=now,
        )

        schedule = ScheduledJobModel(
            id=uuid4(),
            organization_id=organization_id,
            job_type=job_type,
            payload=payload,
            schedule_type=schedule_type,
            schedule_expression=schedule_expression,
            timezone=tz_name,
            next_run_at=next_run,
            last_run_at=None,
            enabled=True,
            created_at=now,
            updated_at=now,
        )
        self.session.add(schedule)
        await self.session.flush()
        logger.info(
            f"Created schedule {schedule.id} for '{job_type}', next run: {next_run}"
        )
        return schedule

    async def list_schedules(
        self,
        organization_id: UUID | None = None,
    ) -> list[ScheduledJobModel]:
        """List active schedules with optional tenant scoping."""
        stmt = select(ScheduledJobModel).order_by(desc(ScheduledJobModel.created_at))
        if organization_id is not None:
            stmt = stmt.where(ScheduledJobModel.organization_id == organization_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_schedule(
        self,
        schedule_id: UUID,
        organization_id: UUID | None = None,
    ) -> ScheduledJobModel | None:
        """Retrieve a specific scheduled job."""
        stmt = select(ScheduledJobModel).where(ScheduledJobModel.id == schedule_id)
        if organization_id is not None:
            stmt = stmt.where(ScheduledJobModel.organization_id == organization_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def disable_schedule(
        self,
        schedule_id: UUID,
        organization_id: UUID | None = None,
    ) -> bool:
        """Disable a schedule."""
        schedule = await self.get_schedule(schedule_id, organization_id)
        if not schedule:
            return False
        schedule.enabled = False
        schedule.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def record_run_and_advance(
        self,
        schedule: ScheduledJobModel,
        job_id: UUID | None = None,
    ) -> bool:
        """Atomically record execution occurrence and advance next_run_at."""
        now = datetime.now(timezone.utc)
        run_key = f"{schedule.id}:{schedule.next_run_at.isoformat()}"

        # Prevent duplicate execution of the exact same slot
        check_stmt = select(ScheduledJobRunModel).where(
            ScheduledJobRunModel.run_key == run_key
        )
        existing = await self.session.execute(check_stmt)
        if existing.scalars().first() is not None:
            logger.warning(f"Occurrence {run_key} already executed. Skipping.")
            return False

        run_record = ScheduledJobRunModel(
            id=uuid4(),
            scheduled_job_id=schedule.id,
            run_key=run_key,
            scheduled_for=schedule.next_run_at,
            executed_at=now,
            status="completed",
            job_id=job_id,
        )
        self.session.add(run_record)

        # Advance schedule
        schedule.last_run_at = now
        if schedule.schedule_type == "once":
            schedule.enabled = False
        else:
            base_time = schedule.next_run_at
            if base_time.tzinfo is None:
                base_time = base_time.replace(tzinfo=timezone.utc)
            schedule.next_run_at = compute_next_run_at(
                schedule_type=schedule.schedule_type,
                expression=schedule.schedule_expression,
                tz_name=schedule.timezone,
                from_time=max(base_time, now),
            )
        schedule.updated_at = now
        await self.session.flush()
        return True
