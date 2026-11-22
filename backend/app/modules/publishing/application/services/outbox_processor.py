"""
Transactional Outbox Processor & Event Dispatcher (ARC-10 §13, WP-ARC10-09).
"""

import asyncio
from collections.abc import Callable
from uuid import UUID

from app.modules.publishing.domain.events import PublicationEvent


class OutboxProcessor:
    """
    Asynchronously claims unpublished outbox events and delivers them to consumers with retry.
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._consumers: dict[str, list[Callable]] = {}
        self._processed_event_ids: set[UUID] = set()
        self.dead_letter_events: list[PublicationEvent] = []

    def register_consumer(self, event_type: str, handler: Callable) -> None:
        self._consumers.setdefault(event_type, []).append(handler)

    async def process_event(self, event: PublicationEvent) -> bool:
        # Idempotency check: don't re-deliver side-effects for already-processed events
        if event.id in self._processed_event_ids:
            return True

        handlers = self._consumers.get(event.event_type, [])
        if not handlers:
            self._processed_event_ids.add(event.id)
            return True

        try:
            for handler in handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            self._processed_event_ids.add(event.id)
            return True
        except Exception as exc:
            event = PublicationEvent(
                id=event.id,
                organization_id=event.organization_id,
                aggregate_type=event.aggregate_type,
                aggregate_id=event.aggregate_id,
                event_type=event.event_type,
                payload=event.payload,
                occurred_at=event.occurred_at,
                attempts=event.attempts + 1,
                last_error_code=str(exc),
            )
            if event.attempts >= self.max_retries:
                self.dead_letter_events.append(event)
            return False

    async def process_batch(self, events: list[PublicationEvent]) -> int:
        delivered_count = 0
        for ev in events:
            success = await self.process_event(ev)
            if success:
                delivered_count += 1
        return delivered_count
