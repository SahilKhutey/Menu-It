"""Domain event primitive defining timestamped, tenant-aware event contracts (FCD-06 §6.4)."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Immutable domain event capturing a notable business occurrence."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = "domain.event"
    schema_version: int = 1
    organization_id: UUID | None = None
    restaurant_id: UUID | None = None
    actor_user_id: UUID | None = None
    correlation_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
