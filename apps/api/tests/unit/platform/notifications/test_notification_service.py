"""Unit tests for NotificationService orchestration and idempotency (FCD-09 WP-03)."""

from uuid import uuid4

import pytest

from menu_it.platform.audit.publisher import InMemoryAuditEventPublisher
from menu_it.platform.notifications.application.service import NotificationService
from menu_it.platform.notifications.domain.contracts import (
    NotificationChannel,
    NotificationMessage,
    NotificationStatus,
)
from menu_it.platform.notifications.infrastructure.email_adapter import (
    EmailNotificationAdapter,
    InMemoryEmailProvider,
)


class MockNotificationRepository:
    """Mock repository for unit testing service delivery tracking and idempotency."""

    def __init__(self) -> None:
        self.in_app_records = []
        self.deliveries = {}

    async def create_in_app(self, **kwargs):
        self.in_app_records.append(kwargs)
        return kwargs

    async def list_in_app_for_user(self, user_id, **kwargs):
        return [r for r in self.in_app_records if r["recipient_user_id"] == user_id]

    async def mark_as_read(self, notification_id, user_id):
        for r in self.in_app_records:
            if r["notification_id"] == notification_id and r["recipient_user_id"] == user_id:
                r["read_at"] = "now"
                return True
        return False

    async def record_delivery(self, **kwargs):
        self.deliveries[kwargs["idempotency_key"]] = type(
            "Delivery",
            (),
            {
                "provider_reference": kwargs.get("provider_reference"),
                "status": kwargs.get("status"),
                "error_code": kwargs.get("error_code"),
            },
        )()

    async def get_delivery_by_idempotency_key(self, key):
        return self.deliveries.get(key)


@pytest.mark.asyncio
async def test_email_notification_dispatch_and_audit():
    """Dispatches email notification, records delivery, and emits audit event."""
    provider = InMemoryEmailProvider()
    adapter = EmailNotificationAdapter(provider=provider)
    repo = MockNotificationRepository()
    audit = InMemoryAuditEventPublisher()

    service = NotificationService(
        adapters={NotificationChannel.EMAIL: adapter},
        repository=repo,
        audit_publisher=audit,
    )

    msg = NotificationMessage(
        notification_id=uuid4(),
        recipient="guest@example.com",
        template_id="account-welcome",
        locale="en",
        variables={"app_name": "Menu-It", "user_name": "Guest"},
        idempotency_key="idem-key-1",
        channel=NotificationChannel.EMAIL,
    )

    res = await service.dispatch(msg)
    assert res.accepted is True
    assert res.status == NotificationStatus.SENT
    assert len(provider.sent) == 1
    assert provider.sent[0].recipient == "guest@example.com"
    assert len(audit.events) == 1
    assert audit.events[0].event_type == "notification.requested"

    # Repeat with same idempotency key -> No duplicate send
    res_repeat = await service.dispatch(msg)
    assert res_repeat.accepted is True
    assert len(provider.sent) == 1  # Still 1


@pytest.mark.asyncio
async def test_in_app_notification_dispatch_and_read():
    """Dispatches in-app notification and marks it as read."""
    repo = MockNotificationRepository()
    user_id = uuid4()
    service = NotificationService(adapters={}, repository=repo)

    msg = NotificationMessage(
        notification_id=uuid4(),
        recipient=str(user_id),
        template_id="account-welcome",
        variables={"user_name": "Admin"},
        idempotency_key="idem-key-2",
        channel=NotificationChannel.IN_APP,
    )

    res = await service.dispatch(msg)
    assert res.accepted is True
    assert res.status == NotificationStatus.DELIVERED
    assert len(repo.in_app_records) == 1

    # List in-app
    listed = await service.list_in_app(recipient_user_id=user_id)
    assert len(listed) == 1
    assert listed[0]["title"] == "Welcome to Menu-It!"

    # Mark as read
    success = await service.mark_in_app_read(msg.notification_id, user_id)
    assert success is True


@pytest.mark.asyncio
async def test_email_failure_handling():
    """Provider failure produces FAILED status and records failure audit."""
    provider = InMemoryEmailProvider()
    provider.should_fail = True
    adapter = EmailNotificationAdapter(provider=provider)
    repo = MockNotificationRepository()
    audit = InMemoryAuditEventPublisher()

    service = NotificationService(
        adapters={NotificationChannel.EMAIL: adapter},
        repository=repo,
        audit_publisher=audit,
    )

    msg = NotificationMessage(
        notification_id=uuid4(),
        recipient="fail@example.com",
        template_id="account-welcome",
        variables={"app_name": "Menu-It", "user_name": "Fail"},
        idempotency_key="idem-key-fail",
        channel=NotificationChannel.EMAIL,
    )

    res = await service.dispatch(msg)
    assert res.accepted is False
    assert res.status == NotificationStatus.FAILED
    assert audit.events[0].event_type == "notification.failed"
