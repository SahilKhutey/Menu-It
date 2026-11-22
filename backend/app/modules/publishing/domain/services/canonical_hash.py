"""
Canonical SHA-256 Hash Computation for ARC-10 Publishing Snapshots & Revisions.
"""

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


def _json_serial_default(obj: Any) -> Any:
    """Helper to ensure canonical serialization of datetimes, decimals, and UUIDs."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return f"{obj:.2f}"
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable for canonical hash")


def calculate_snapshot_hash(snapshot: dict[str, Any]) -> str:
    """
    Computes deterministic SHA-256 digest over normalized canonical JSON (ARC-10 §7.3).
    """
    canonical_json = json.dumps(
        snapshot,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=_json_serial_default,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
