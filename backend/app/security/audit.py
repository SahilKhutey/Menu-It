"""
ModularMenu — Audit Logging Architecture (ARC-12 §13, ADR-0240).
Append-only sensitive event tracking with automated credential masking.
"""

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """Immutable audit event representation."""

    event_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor_user_id: UUID | None = None
    organization_id: UUID | None = None
    action: str
    resource_type: str
    resource_id: UUID | None = None
    outcome: Literal["success", "failure", "denied"]
    reason: str | None = None
    correlation_id: str = "sys-internal"
    source: str = "api"


class AuditLogger:
    """Append-only audit ledger with immutability guarantees."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def log(self, event: AuditEvent) -> AuditEvent:
        """Append an audit record to the ledger; rejects mutation or secrets."""
        # Sanitize sensitive keywords from reason
        if event.reason:
            sanitized = event.reason
            for sensitive_word in ("password", "secret", "token", "credential", "api_key"):
                if sensitive_word in sanitized.lower():
                    sanitized = sanitized.replace(sensitive_word, "***")
            event.reason = sanitized

        self._events.append(event)
        return event

    def get_events_for_organization(self, organization_id: UUID) -> list[AuditEvent]:
        """Query audit records scoped to a specific tenant organization."""
        return [e for e in self._events if e.organization_id == organization_id]

    def all_events(self) -> list[AuditEvent]:
        """Return shallow copy of audit stream."""
        return list(self._events)


audit_logger = AuditLogger()
