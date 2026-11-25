"""Unit tests for audit event contracts and publishers (FCD-09 WP-05)."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from menu_it.platform.audit.contracts import AuditEvent
from menu_it.platform.audit.publisher import InMemoryAuditEventPublisher, LoggingAuditEventPublisher


@pytest.mark.asyncio
async def test_audit_event_immutability_and_redaction():
    """AuditEvent enforces UTC awareness, immutability, and automatic metadata redaction."""
    event_id = uuid4()
    org_id = uuid4()
    actor_id = uuid4()

    event = AuditEvent(
        event_id=event_id,
        event_type="file.uploaded",
        occurred_at=datetime.now(UTC),
        organization_id=org_id,
        actor_user_id=actor_id,
        resource_type="file",
        resource_id="file-123",
        action="upload",
        outcome="success",
        correlation_id="corr-abc",
        metadata={
            "filename": "menu.pdf",
            "password": "should_be_redacted",
            "auth_secret_key": "secret_abc",
        },
    )

    assert event.event_type == "file.uploaded"
    assert event.metadata["filename"] == "menu.pdf"
    assert event.metadata["password"] == "[REDACTED]"
    assert event.metadata["auth_secret_key"] == "[REDACTED]"

    with pytest.raises(Exception):
        event.action = "modified"  # type: ignore[misc]

    with pytest.raises(ValueError, match="occurred_at must be timezone-aware"):
        AuditEvent(
            event_id=event_id,
            event_type="test",
            occurred_at=datetime(2026, 11, 25, 10, 0, 0),  # naive
            organization_id=None,
            actor_user_id=None,
            resource_type="system",
            resource_id=None,
            action="init",
            outcome="success",
        )


@pytest.mark.asyncio
async def test_in_memory_and_logging_audit_publishers():
    """Publishers accept and process audit events properly."""
    in_memory = InMemoryAuditEventPublisher()
    logging_pub = LoggingAuditEventPublisher()

    event = AuditEvent(
        event_id=uuid4(),
        event_type="config.updated",
        occurred_at=datetime.now(UTC),
        organization_id=None,
        actor_user_id=None,
        resource_type="config",
        resource_id="api_port",
        action="update",
        outcome="success",
        metadata={"old": 8000, "new": 8080},
    )

    await in_memory.publish(event)
    assert len(in_memory.events) == 1
    assert in_memory.events[0].resource_id == "api_port"

    await logging_pub.publish(event)  # Should not raise
