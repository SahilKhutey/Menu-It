"""Event domain contracts and serialization envelopes (FCD-10 WP-05)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Standardized serialization envelope for transactional domain events."""

    event_id: UUID
    event_type: str
    schema_version: int
    occurred_at: datetime
    organization_id: UUID | None
    actor_user_id: UUID | None
    correlation_id: str
    payload: dict[str, Any]
