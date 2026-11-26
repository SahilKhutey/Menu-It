"""Tests for durable security audit logging (FCD-11 WP-07)."""

import uuid

import pytest

from menu_it.platform.audit.writer import SecurityAuditWriter, SecurityEvent


def test_security_event_redaction_and_defaults() -> None:
    event = SecurityEvent(
        event_type="auth.login.failed",
        outcome="failure",
        resource_type="user",
        action="login",
        metadata={
            "ip": "127.0.0.1",
            "password": "SuperSecretPassword123",
            "token": "sensitive-token-val",
            "attempt": 1,
        },
    )

    assert event.event_id is not None
    assert event.occurred_at.tzinfo is not None
    # Verify metadata is automatically redacted
    assert event.metadata["password"] == "[REDACTED]"
    assert event.metadata["token"] == "[REDACTED]"
    assert event.metadata["attempt"] == 1


@pytest.mark.asyncio
async def test_security_audit_writer_fallback_without_session() -> None:
    writer = SecurityAuditWriter(session=None)
    event = SecurityEvent(
        event_type="auth.password_reset.requested",
        outcome="success",
        resource_type="credential",
        action="reset_request",
        correlation_id=str(uuid.uuid4()),
        reason_code="USER_INITIATED",
    )

    model = await writer.write(event)
    assert model.event_id == event.event_id
    assert model.event_type == "auth.password_reset.requested"
    assert model.outcome == "success"
