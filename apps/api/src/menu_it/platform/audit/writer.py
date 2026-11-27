"""Durable security audit writer and persistence engine (FCD-11 WP-07)."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.security_audit import SecurityAuditEventModel
from menu_it.platform.common.redaction import redact_mapping

logger = logging.getLogger("menu_it.security.audit")


@dataclass(frozen=True)
class SecurityEvent:
    """Security audit event record prior to persistence."""

    event_type: str
    outcome: str
    resource_type: str
    action: str
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    actor_user_id: uuid.UUID | None = None
    actor_type: str = "user"
    organization_id: uuid.UUID | None = None
    restaurant_id: uuid.UUID | None = None
    resource_id: str | None = None
    correlation_id: str | None = None
    source_ip: str | None = None
    user_agent: str | None = None
    reason_code: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.occurred_at.tzinfo is None:
            object.__setattr__(self, "occurred_at", self.occurred_at.replace(tzinfo=UTC))
        # Ensure metadata is securely redacted
        object.__setattr__(self, "metadata", redact_mapping(self.metadata))


class SecurityAuditWriter:
    """Durable writer for security events to PostgreSQL security_audit_events."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    async def write(
        self,
        event: SecurityEvent,
        *,
        session: AsyncSession | None = None,
    ) -> SecurityAuditEventModel:
        """Persist a security audit record to the database with structured log fallback."""
        active_session = session or self.session
        model = SecurityAuditEventModel(
            id=uuid.uuid4(),
            event_id=event.event_id,
            occurred_at=event.occurred_at,
            event_type=event.event_type,
            outcome=event.outcome,
            actor_user_id=event.actor_user_id,
            actor_type=event.actor_type,
            organization_id=event.organization_id,
            restaurant_id=event.restaurant_id,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            action=event.action,
            correlation_id=event.correlation_id,
            source_ip=event.source_ip,
            user_agent=event.user_agent,
            reason_code=event.reason_code,
            metadata_json=event.metadata,
        )

        if active_session is not None:
            try:
                active_session.add(model)
                await active_session.flush()
                return model
            except Exception as exc:
                logger.error(
                    "Failed to persist security audit event %s to database: %s",
                    event.event_id,
                    exc,
                    extra={
                        "event_type": event.event_type,
                        "outcome": event.outcome,
                        "correlation_id": event.correlation_id,
                        "organization_id": str(event.organization_id),
                    },
                )

        # Fallback structured log emission when DB session is unavailable or flush fails
        logger.warning(
            "Security audit event written via fallback log: %s",
            event.event_type,
            extra={
                "event_id": str(event.event_id),
                "occurred_at": event.occurred_at.isoformat(),
                "event_type": event.event_type,
                "outcome": event.outcome,
                "actor_user_id": str(event.actor_user_id) if event.actor_user_id else None,
                "actor_type": event.actor_type,
                "organization_id": str(event.organization_id) if event.organization_id else None,
                "restaurant_id": str(event.restaurant_id) if event.restaurant_id else None,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "action": event.action,
                "correlation_id": event.correlation_id,
                "reason_code": event.reason_code,
            },
        )
        return model
