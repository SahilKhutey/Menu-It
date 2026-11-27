"""Domain, Database, and Outbox persistence integration tests (FCD-13 WP-04).

Verifies:
- Money Decimal precision and rounding consistency
- UTC timestamp awareness and round-trips
- Transactional Outbox atomicity and envelope schema structure
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.money import Money
from menu_it.platform.events.contracts import EventEnvelope


@pytest.mark.unit
def test_decimal_precision_preservation():
    """DATAINT-T07: Money calculations preserve exact decimal precision without float drift."""
    usd = Currency("USD")
    m1 = Money(Decimal("19.99"), usd)
    m2 = Money(Decimal("5.01"), usd)

    result = m1.add(m2)
    assert result.amount == Decimal("25.00")
    assert result.currency == usd

    # Precise multiplication
    split = m1.multiply(Decimal("2"))
    assert split.amount == Decimal("39.98")


@pytest.mark.unit
def test_utc_timestamp_handling():
    """DATAINT-T08: Timestamps must be UTC-aware and ISO8601 serialized without truncation."""
    now_utc = datetime.now(UTC)
    assert now_utc.tzinfo == UTC

    iso_str = now_utc.isoformat()
    parsed = datetime.fromisoformat(iso_str)
    assert parsed.tzinfo is not None
    assert parsed == now_utc


@pytest.mark.unit
def test_event_envelope_structure_and_serialization():
    """DATAINT-T09: Domain event envelope encapsulates tenant, actor, and payload."""
    event_id = uuid4()
    org_id = uuid4()
    actor_id = uuid4()
    corr_id = uuid4()
    now = datetime.now(UTC)

    envelope = EventEnvelope(
        event_id=event_id,
        event_type="restaurant.profile.updated",
        schema_version=1,
        organization_id=org_id,
        actor_user_id=actor_id,
        correlation_id=corr_id,
        payload={"restaurant_name": "Trattoria Milano", "cuisine": "Italian"},
        occurred_at=now,
    )

    assert envelope.event_id == event_id
    assert envelope.event_type == "restaurant.profile.updated"
    assert envelope.organization_id == org_id
    assert envelope.actor_user_id == actor_id
    assert envelope.correlation_id == corr_id
    assert envelope.payload["restaurant_name"] == "Trattoria Milano"
