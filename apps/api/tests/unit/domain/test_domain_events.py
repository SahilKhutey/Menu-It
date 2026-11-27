"""Unit tests for DomainEvent immutable structure (FCD-06 §6.4)."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from menu_it.domain.base.domain_event import DomainEvent


def test_domain_event_defaults() -> None:
    org_id = uuid4()
    event = DomainEvent(
        event_type="test.event.v1",
        organization_id=org_id,
        payload={"message": "hello"},
    )

    assert isinstance(event.event_id, UUID)
    assert isinstance(event.occurred_at, datetime)
    assert event.occurred_at.tzinfo == UTC
    assert event.event_type == "test.event.v1"
    assert event.organization_id == org_id
    assert event.payload == {"message": "hello"}


def test_domain_event_is_immutable() -> None:
    event = DomainEvent(event_type="test.event.v1")
    with pytest.raises(AttributeError):
        event.event_type = "altered.v1"  # type: ignore[misc]
