"""Cache JSON serialization and deserialization utilities (FCD-10 WP-02)."""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


class CacheJSONEncoder(json.JSONEncoder):
    """Safe JSON encoder handling UUID, datetime, date, and Decimal."""

    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


def serialize_for_cache(value: Any) -> bytes:
    """Serialize a Python data structure to UTF-8 encoded JSON bytes."""
    return json.dumps(
        value,
        cls=CacheJSONEncoder,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def deserialize_from_cache(raw: bytes) -> Any:
    """Safely deserialize raw UTF-8 bytes to Python objects."""
    return json.loads(raw.decode("utf-8"))
