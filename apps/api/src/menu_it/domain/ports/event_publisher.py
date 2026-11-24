"""Domain event publisher port (FCD-06 §11.3)."""

from typing import Protocol

from menu_it.domain.base.domain_event import DomainEvent


class DomainEventPublisher(Protocol):
    """Port for publishing committed domain events."""

    async def publish(self, events: list[DomainEvent]) -> None:
        """Publish a batch of domain events to outbox or event bus."""
        ...
