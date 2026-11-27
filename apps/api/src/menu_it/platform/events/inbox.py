"""Consumer inbox event deduplication service (FCD-10 WP-05)."""

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.processed_event import ProcessedEventModel

logger = logging.getLogger("menu_it.platform.events.inbox")


class EventInbox:
    """Consumer inbox providing at-most-once idempotent processing guarantees."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record_if_not_processed(
        self,
        consumer_name: str,
        event_id: UUID,
    ) -> bool:
        """Check and mark event as processed.

        Returns True if first time processing (proceed with work).
        Returns False if already processed (duplicate delivery, skip safely).
        """
        # Check existing
        stmt = select(ProcessedEventModel).where(
            ProcessedEventModel.consumer_name == consumer_name,
            ProcessedEventModel.event_id == event_id,
        )
        result = await self.session.execute(stmt)
        if result.scalars().first() is not None:
            logger.info(f"Duplicate event {event_id} suppressed for consumer '{consumer_name}'.")
            return False

        # Record in inbox
        record = ProcessedEventModel(
            consumer_name=consumer_name,
            event_id=event_id,
            processed_at=datetime.now(UTC),
        )
        self.session.add(record)
        await self.session.flush()
        return True
