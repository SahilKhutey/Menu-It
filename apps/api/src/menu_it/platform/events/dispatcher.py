"""Transactional outbox dispatcher service (FCD-10 WP-05)."""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.event_outbox import EventOutboxModel
from menu_it.platform.events.contracts import EventEnvelope
from menu_it.platform.events.registry import get_consumers
from menu_it.platform.jobs.retry import calculate_retry_delay

logger = logging.getLogger("menu_it.platform.events.dispatcher")


class OutboxDispatcher:
    """Dispatches unpublished outbox events to registered consumers or worker queue."""

    def __init__(self, session: AsyncSession, services: Any = None) -> None:
        self.session = session
        self.services = services

    async def claim_batch(self, batch_size: int = 100) -> list[EventOutboxModel]:
        """Claim a batch of pending events using FOR UPDATE SKIP LOCKED where supported."""
        now = datetime.now(UTC)
        stmt = (
            select(EventOutboxModel)
            .where(
                EventOutboxModel.published_at.is_(None),
                or_(
                    EventOutboxModel.next_attempt_at.is_(None),
                    EventOutboxModel.next_attempt_at <= now,
                ),
            )
            .order_by(EventOutboxModel.occurred_at)
            .limit(batch_size)
        )

        # Apply skip_locked only if supported by dialect
        bind = self.session.bind
        if bind and "postgresql" in bind.dialect.name:
            stmt = stmt.with_for_update(skip_locked=True)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def dispatch_event(self, record: EventOutboxModel) -> bool:
        """Deliver outbox event to registered consumer handlers."""
        now = datetime.now(UTC)
        envelope = EventEnvelope(
            event_id=record.event_id,
            event_type=record.event_type,
            schema_version=record.schema_version,
            occurred_at=record.occurred_at,
            organization_id=record.organization_id,
            actor_user_id=record.actor_user_id,
            correlation_id=record.correlation_id,
            payload=record.payload,
        )

        consumers = get_consumers(record.event_type)
        if not consumers:
            # No consumers registered; mark as published to prevent repeated scans
            record.published_at = now
            await self.session.flush()
            return True

        try:
            import inspect

            for consumer in consumers:
                if inspect.iscoroutinefunction(consumer):
                    await consumer(envelope, self.services)
                else:
                    res = consumer(envelope, self.services)
                    if inspect.isawaitable(res):
                        await res

            record.published_at = now
            await self.session.flush()
            logger.info(
                f"Successfully published outbox event {record.event_id} ({record.event_type})"
            )
            return True
        except Exception as exc:
            record.attempts += 1
            delay = calculate_retry_delay(record.attempts, initial_delay=5, maximum_delay=600)
            record.next_attempt_at = datetime.fromtimestamp(now.timestamp() + delay, tz=UTC)
            record.last_error_code = type(exc).__name__
            await self.session.flush()
            msg = (
                f"Failed to publish event {record.event_id}: {exc}. "
                f"Next retry scheduled at {record.next_attempt_at}"
            )
            logger.warning(msg)
            return False

    async def process_batch(self, batch_size: int = 100) -> int:
        """Claim and dispatch a batch of pending outbox events."""
        records = await self.claim_batch(batch_size=batch_size)
        published_count = 0
        for rec in records:
            success = await self.dispatch_event(rec)
            if success:
                published_count += 1
        return published_count
