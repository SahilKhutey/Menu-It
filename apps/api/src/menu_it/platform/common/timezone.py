"""IANA Timezone resolution and local time conversion (FCD-09 WP-06)."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def get_timezone(name: str) -> ZoneInfo:
    """Resolve an IANA timezone name or raise ValueError."""
    if not name or not isinstance(name, str):
        raise ValueError("Timezone name must be a non-empty string.")
    try:
        return ZoneInfo(name.strip())
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"Unsupported IANA timezone: '{name}'.") from exc


def to_local_time(value: datetime, timezone_name: str) -> datetime:
    """Convert a timezone-aware UTC datetime to a specified IANA local timezone."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Datetime must be timezone-aware.")
    tz = get_timezone(timezone_name)
    return value.astimezone(tz)


def now_in_timezone(timezone_name: str) -> datetime:
    """Return the current moment converted to the specified local timezone."""
    tz = get_timezone(timezone_name)
    return datetime.now(UTC).astimezone(tz)
