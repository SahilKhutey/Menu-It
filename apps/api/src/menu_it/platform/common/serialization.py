"""Safe primitive and domain object serialization (FCD-09 WP-06)."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


def serialize_value(value: Any) -> Any:
    """Recursively serialize decimals, datetimes, UUIDs, dicts, and lists safely."""
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("Non-finite Decimal is not serializable.")
        return format(value, "f")
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must be timezone-aware.")
        return value.astimezone(UTC).isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serialize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serialize_value(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"Unsupported serialization type: {type(value).__name__}")
