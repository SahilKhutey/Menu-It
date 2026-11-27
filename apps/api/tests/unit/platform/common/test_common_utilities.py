"""Unit tests for platform common utilities (FCD-09 WP-06)."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

import pytest

from menu_it.platform.common.clock import FrozenClock, SystemClock
from menu_it.platform.common.identifiers import new_uuid, parse_uuid
from menu_it.platform.common.localization import resolve_locale
from menu_it.platform.common.pagination import PageRequest
from menu_it.platform.common.serialization import serialize_value
from menu_it.platform.common.timezone import get_timezone, now_in_timezone, to_local_time


def test_clock_system_and_frozen():
    """System clock returns UTC now; Frozen clock supports pinning and advancing."""
    sys_clock = SystemClock()
    t1 = sys_clock.now()
    assert t1.tzinfo is UTC

    fixed = datetime(2026, 11, 25, 12, 0, 0, tzinfo=UTC)
    frozen = FrozenClock(fixed)
    assert frozen.now() == fixed

    frozen.advance(timedelta(minutes=30))
    assert frozen.now() == datetime(2026, 11, 25, 12, 30, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="timezone-aware"):
        FrozenClock(datetime(2026, 11, 25, 12, 0, 0))  # naive


def test_uuid_generation_and_parsing():
    """Generates valid UUIDs and parses strings correctly."""
    u = new_uuid()
    assert isinstance(u, UUID)

    parsed = parse_uuid(str(u))
    assert parsed == u
    assert parse_uuid(u) == u

    with pytest.raises(ValueError, match="Invalid UUID format"):
        parse_uuid("not-a-valid-uuid")


def test_timezone_resolution_and_conversion():
    """Resolves IANA timezone and converts UTC time accurately."""
    tz = get_timezone("Asia/Kolkata")
    assert tz.key == "Asia/Kolkata"

    utc_dt = datetime(2026, 11, 25, 10, 0, 0, tzinfo=UTC)
    kolkata_dt = to_local_time(utc_dt, "Asia/Kolkata")
    # IST is UTC+5:30
    assert kolkata_dt.hour == 15
    assert kolkata_dt.minute == 30

    current_ist = now_in_timezone("Asia/Kolkata")
    assert current_ist.tzinfo is not None

    with pytest.raises(ValueError, match="Unsupported IANA timezone"):
        get_timezone("Invalid/Unknown_Zone")

    with pytest.raises(ValueError, match="must be timezone-aware"):
        to_local_time(datetime(2026, 11, 25, 10, 0, 0), "Asia/Kolkata")


def test_serialization_primitives_and_containers():
    """Serializes Decimal, UUID, aware datetime, dicts, and lists safely."""
    data = {
        "price": Decimal("499.50"),
        "id": UUID("12345678-1234-5678-1234-567812345678"),
        "created_at": datetime(2026, 11, 25, 9, 30, 0, tzinfo=UTC),
        "tags": ["food", "spicy"],
        "count": 5,
        "is_active": True,
    }
    serialized = serialize_value(data)
    assert serialized["price"] == "499.50"
    assert serialized["id"] == "12345678-1234-5678-1234-567812345678"
    assert serialized["created_at"] == "2026-11-25T09:30:00+00:00"
    assert serialized["tags"] == ["food", "spicy"]

    with pytest.raises(ValueError, match="Non-finite Decimal"):
        serialize_value(Decimal("NaN"))

    with pytest.raises(ValueError, match="must be timezone-aware"):
        serialize_value(datetime(2026, 11, 25, 9, 0, 0))

    with pytest.raises(TypeError, match="Unsupported serialization type"):
        serialize_value(object())


def test_pagination_validation_and_offset():
    """PageRequest bounds validation and offset calculation."""
    p1 = PageRequest(page=1, page_size=20)
    assert p1.offset == 0

    p2 = PageRequest(page=3, page_size=15)
    assert p2.offset == 30

    with pytest.raises(ValueError, match="Page must be at least 1"):
        PageRequest(page=0, page_size=20)

    with pytest.raises(ValueError, match="Page size must be between 1 and 100"):
        PageRequest(page=1, page_size=0)

    with pytest.raises(ValueError, match="Page size must be between 1 and 100"):
        PageRequest(page=1, page_size=101)


def test_locale_resolution():
    """Resolves language codes and falls back to default."""
    assert resolve_locale("en") == "en"
    assert resolve_locale("en-US") == "en"
    assert resolve_locale("hi") == "hi"
    assert resolve_locale("hi_IN") == "hi"
    assert resolve_locale("fr-FR") == "en"  # unsupported fallback
    assert resolve_locale(None) == "en"
    assert resolve_locale("", default="hi") == "hi"
