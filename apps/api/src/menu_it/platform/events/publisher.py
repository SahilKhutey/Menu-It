"""Transactional outbox event publisher (FCD-10 WP-05)."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.event_outbox import EventOutboxModel
from menu_it.platform.events.contracts import EventEnvelope

logger = logging.getLogger("menu_it.platform.events.publisher")


class OutboxEventPublisher:
    """Publishes domain events to the PostgreSQL event_outbox within the active transaction."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def publish(self, event: EventEnvelope) -> EventOutboxModel:
        """Add event to outbox. Does NOT independently commit; caller controls transaction."""
        record = EventOutboxModel(
            id=event.event_id,
            event_id=event.event_id,
            event_type=event.event_type,
            schema_version=event.schema_version,
            organization_id=event.organization_id,
            actor_user_id=event.actor_user_id,
            correlation_id=event.correlation_id,
            payload=event.payload,
            occurred_at=event.occurred_at,
            published_at=None,
            attempts=0,
            next_attempt_at=None,
        )
        self.session.add(record)
        # Flush to register in active transaction without committing
        await self.session.flush()
        logger.debug(f"Queued outbox event {event.event_id} ({event.event_type})")
        return record
