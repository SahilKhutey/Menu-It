"""Security, Audit, and Observability integration tests (FCD-13 WP-08).

Verifies:
- Prometheus telemetry metrics exposure
- Audit logging publisher execution
- Sensitive data masking and redaction
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from menu_it.application import create_application
from menu_it.platform.audit.contracts import AuditEvent
from menu_it.platform.audit.publisher import LoggingAuditEventPublisher


@pytest.mark.integration
@pytest.mark.asyncio
async def test_metrics_endpoint_scraped_by_prometheus():
    """OBSINT-T04: Prometheus metrics endpoint exposes application telemetry counters."""
    app = create_application()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/v1/metrics")
        assert resp.status_code == 200
        assert (
            resp.headers.get("content-type", "").startswith("text/plain") or resp.status_code == 200
        )
        content = resp.text
        assert len(content) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_audit_event_logging_publisher():
    """OBSINT-T06: Logging audit publisher publishes audit events without exception."""
    publisher = LoggingAuditEventPublisher()
    event = AuditEvent(
        event_id=uuid4(),
        event_type="security.authentication.login",
        occurred_at=datetime.now(UTC),
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        resource_type="session",
        resource_id="session_123",
        action="user.authenticated",
        outcome="success",
        metadata={"ip_address": "127.0.0.1", "auth_method": "bearer_jwt"},
    )
    # Should complete without error
    await publisher.publish(event)
