"""Audit event publishers for testing and standard application logging (FCD-09 WP-05)."""

import logging
from typing import Any

from menu_it.platform.audit.contracts import AuditEvent, AuditEventPublisher

logger = logging.getLogger("menu_it.platform.audit")


class InMemoryAuditEventPublisher:
    """In-memory audit publisher collecting events for test verification."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    async def publish(self, event: AuditEvent) -> None:
        self.events.append(event)

    def clear(self) -> None:
        self.events.clear()


class LoggingAuditEventPublisher:
    """Audit publisher logging structured audit records to the application logger."""

    async def publish(self, event: AuditEvent) -> None:
        extra_data: dict[str, Any] = {
            "audit_event_id": str(event.event_id),
            "event_type": event.event_type,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "action": event.action,
            "outcome": event.outcome,
            "metadata": event.metadata,
        }
        logger.info(
            "AUDIT_EVENT: %s on %s:%s by actor %s (outcome=%s)",
            event.action,
            event.resource_type,
            event.resource_id,
            event.actor_user_id,
            event.outcome,
            extra={
                "extra_data": extra_data,
                "request_id": event.correlation_id,
                "organization_id": str(event.organization_id) if event.organization_id else None,
                "user_id": str(event.actor_user_id) if event.actor_user_id else None,
            },
        )
