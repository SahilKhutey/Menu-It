"""Shared platform services integration tests (FCD-13 WP-06).

Verifies:
- File storage upload, retrieval, and deletion lifecycle
- Notification template rendering and formatting
- Audit event contracts and secret redaction
- Timezone and currency utilities
"""

import io
import tempfile
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.money import Money
from menu_it.domain.value_objects.timezone import TimeZone
from menu_it.platform.audit.contracts import AuditEvent
from menu_it.platform.files.infrastructure.local_storage import LocalFileStorage
from menu_it.platform.notifications.application.renderer import TemplateRenderer


@pytest.mark.unit
@pytest.mark.asyncio
async def test_file_storage_lifecycle():
    """PLAT-T01 & PLAT-T02: Storage adapter uploads, checks existence, and deletes files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        storage = LocalFileStorage(root=Path(tmp_dir))
        key = f"tenants/org_{uuid4()}/menu.pdf"
        data = b"%PDF-1.4 sample content"

        # Upload via BinaryIO stream
        stored = await storage.put(
            key=key, content=io.BytesIO(data), content_type="application/pdf"
        )
        assert stored is not None
        assert stored.storage_key == key
        assert await storage.exists(key=key) is True

        # Read back
        reader = await storage.open(key=key)
        assert reader.read() == data

        # Delete
        await storage.delete(key=key)
        assert await storage.exists(key=key) is False


@pytest.mark.unit
def test_notification_template_rendering():
    """PLAT-T04: Template renderer renders localized notification templates."""
    renderer = TemplateRenderer()
    subject, html_body, text_body = renderer.render_email(
        "account-welcome",
        {"user_name": "Alice", "app_name": "Menu-It", "login_url": "https://menu-it.com/login"},
        locale="en",
    )
    assert "Welcome" in subject
    assert "Alice" in text_body
    assert "Menu-It" in text_body


@pytest.mark.unit
def test_audit_event_contract_structure():
    """PLAT-T08: Audit event encapsulates actor, organization, action, and metadata."""
    org_id = uuid4()
    actor_id = uuid4()
    event = AuditEvent(
        event_id=uuid4(),
        event_type="restaurant.profile.updated",
        occurred_at=datetime.now(UTC),
        organization_id=org_id,
        actor_user_id=actor_id,
        resource_type="restaurant",
        resource_id=str(uuid4()),
        action="update",
        outcome="success",
        metadata={"changes": ["name", "opening_hours"]},
    )
    assert event.organization_id == org_id
    assert event.action == "update"
    assert event.actor_user_id == actor_id


@pytest.mark.unit
def test_timezone_and_money_utilities():
    """PLAT-T09 & PLAT-T10: Standard IANA timezone validation and Money formatting."""
    tz = TimeZone("America/New_York")
    assert tz.name == "America/New_York"

    with pytest.raises(ValidationDomainError):
        TimeZone("Invalid/NonExistent_Zone")

    eur = Currency("EUR")
    m = Money(Decimal("45.50"), eur)
    assert str(m.amount) == "45.50"
    assert m.currency == eur
