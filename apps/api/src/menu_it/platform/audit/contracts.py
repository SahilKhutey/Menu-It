"""Audit event domain contracts and publisher protocol (FCD-09 WP-05)."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from menu_it.platform.common.redaction import redact_mapping


@dataclass(frozen=True)
class AuditEvent:
    """Immutable audit record representing a significant business or security event."""

    event_id: UUID
    event_type: str
    occurred_at: datetime
    organization_id: UUID | None
    actor_user_id: UUID | None
    resource_type: str
    resource_id: str | None
    action: str
    outcome: str
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware (UTC).")
        # Ensure metadata is safe from sensitive leaks
        redacted = redact_mapping(self.metadata)
        object.__setattr__(self, "metadata", redacted)


@runtime_checkable
class AuditEventPublisher(Protocol):
    """Protocol for dispatching audit events to persistence or stream sinks."""

    async def publish(self, event: AuditEvent) -> None:
        """Publish an audit event."""
        ...
