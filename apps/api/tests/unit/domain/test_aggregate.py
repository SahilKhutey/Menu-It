"""Unit tests for AggregateRoot and domain event recording (FCD-06 §6.3)."""

from uuid import uuid4

from menu_it.domain.base.aggregate import AggregateRoot
from menu_it.domain.base.domain_event import DomainEvent


class SampleAggregate(AggregateRoot):
    pass


def test_aggregate_records_and_collects_events() -> None:
    agg_id = uuid4()
    aggregate = SampleAggregate(id=agg_id)

    event1 = DomainEvent(event_type="sample.created.v1", payload={"foo": "bar"})
    event2 = DomainEvent(event_type="sample.updated.v1", payload={"key": 123})

    aggregate.record_event(event1)
    aggregate.record_event(event2)

    events = aggregate.collect_events()
    assert len(events) == 2
    assert events[0] == event1
    assert events[1] == event2

    # Verify collecting clears uncommitted events
    assert len(aggregate.collect_events()) == 0
