"""Persistent job scheduler polling and dispatch loop (FCD-10 WP-07)."""

from datetime import datetime, timezone
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.scheduled_job import ScheduledJobModel
from menu_it.platform.jobs.contracts import JobContext
from menu_it.platform.jobs.service import JobService
from menu_it.platform.scheduling.service import SchedulingService

logger = logging.getLogger("menu_it.platform.scheduling.scheduler")


class JobScheduler:
    """Claims due persistent schedules and submits corresponding background execution jobs."""

    def __init__(
        self,
        session: AsyncSession,
        job_service: JobService,
    ) -> None:
        self.session = session
        self.job_service = job_service
        self.scheduling_service = SchedulingService(session)

    async def get_due_schedules(self, limit: int = 50) -> list[ScheduledJobModel]:
        """Fetch active schedules whose next_run_at has arrived."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(ScheduledJobModel)
            .where(
                ScheduledJobModel.enabled.is_(True),
                ScheduledJobModel.next_run_at <= now,
            )
            .order_by(ScheduledJobModel.next_run_at)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def process_due_schedules(self) -> int:
        """Scan and execute all due schedules."""
        schedules = await self.get_due_schedules()
        executed_count = 0

        for sched in schedules:
            context = JobContext(
                organization_id=sched.organization_id,
                actor_user_id=None,
                correlation_id=f"sched-{sched.id}",
                initiated_by="scheduler",
            )
            try:
                envelope = await self.job_service.submit_job(
                    job_type=sched.job_type,
                    payload=sched.payload,
                    context=context,
                )
                success = await self.scheduling_service.record_run_and_advance(
                    schedule=sched,
                    job_id=envelope.job_id,
                )
                if success:
                    executed_count += 1
            except Exception as exc:
                logger.error(f"Error executing schedule {sched.id}: {exc}", exc_info=True)

        return executed_count
