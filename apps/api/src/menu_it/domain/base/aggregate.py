"""Aggregate root primitive coordinating transactional invariant boundaries (FCD-06 §6.3)."""

from dataclasses import dataclass, field

from menu_it.domain.base.domain_event import DomainEvent
from menu_it.domain.base.entity import Entity


@dataclass(eq=False)
class AggregateRoot(Entity):
    """Entry point for state mutations within an invariant boundary."""

    _domain_events: list[DomainEvent] = field(
        default_factory=list,
        init=False,
        repr=False,
        compare=False,
    )

    def record_event(self, event: DomainEvent) -> None:
        """Record an uncommitted domain event emitted during a state mutation."""
        self._domain_events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        """Collect and clear all recorded uncommitted domain events."""
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
