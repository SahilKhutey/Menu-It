"""Notification orchestration service (FCD-09 WP-03)."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from menu_it.platform.audit.contracts import AuditEvent, AuditEventPublisher
from menu_it.platform.common.identifiers import parse_uuid
from menu_it.platform.notifications.application.renderer import TemplateRenderer
from menu_it.platform.notifications.domain.contracts import (
    NotificationChannel,
    NotificationChannelAdapter,
    NotificationMessage,
    NotificationResult,
    NotificationStatus,
)
from menu_it.platform.notifications.infrastructure.repository import NotificationRepository


class NotificationService:
    """Orchestrates notification validation, templating, idempotency, and dispatch."""

    def __init__(
        self,
        adapters: dict[NotificationChannel, NotificationChannelAdapter],
        repository: NotificationRepository | None = None,
        renderer: TemplateRenderer | None = None,
        audit_publisher: AuditEventPublisher | None = None,
    ) -> None:
        self.adapters = adapters
        self.repository = repository
        self.renderer = renderer or TemplateRenderer()
        self.audit_publisher = audit_publisher

    async def dispatch(self, message: NotificationMessage) -> NotificationResult:
        """Send a notification idempotently across the requested channel."""
        # 1. Idempotency Check
        if self.repository and message.idempotency_key:
            existing = await self.repository.get_delivery_by_idempotency_key(
                message.idempotency_key
            )
            if existing:
                return NotificationResult(
                    provider_reference=existing.provider_reference,
                    accepted=existing.status
                    in (NotificationStatus.ACCEPTED, NotificationStatus.SENT),
                    status=NotificationStatus(existing.status),
                    error=existing.error_code,
                )

        # 2. Dispatch by Channel
        if message.channel == NotificationChannel.IN_APP:
            result = await self._dispatch_in_app(message)
        else:
            adapter = self.adapters.get(message.channel)
            if adapter is None:
                raise ValueError(f"Unsupported notification channel: '{message.channel}'.")
            result = await adapter.send(message)

        # 3. Record Delivery Outcome
        if self.repository and message.idempotency_key:
            await self.repository.record_delivery(
                delivery_id=uuid4(),
                notification_id=message.notification_id,
                channel=str(message.channel),
                status=str(result.status),
                provider_reference=result.provider_reference,
                idempotency_key=message.idempotency_key,
                error_code=result.error,
            )

        # 4. Audit Tracking
        if self.audit_publisher:
            outcome = "success" if result.accepted else "failure"
            await self.audit_publisher.publish(
                AuditEvent(
                    event_id=uuid4(),
                    event_type="notification.requested"
                    if result.accepted
                    else "notification.failed",
                    occurred_at=datetime.now(UTC),
                    organization_id=message.organization_id,
                    actor_user_id=None,
                    resource_type="notification",
                    resource_id=str(message.notification_id),
                    action=f"dispatch_{message.channel}",
                    outcome=outcome,
                    metadata={
                        "recipient": message.recipient,
                        "template_id": message.template_id,
                        "channel": str(message.channel),
                        "status": str(result.status),
                    },
                )
            )

        return result

    async def _dispatch_in_app(self, message: NotificationMessage) -> NotificationResult:
        """Render in-app template and persist in notifications table."""
        if not self.repository:
            raise RuntimeError("NotificationRepository required for in-app notifications.")

        recipient_uuid = parse_uuid(message.recipient)
        title, body = self.renderer.render_in_app(
            template_id=message.template_id,
            variables=message.variables,
            locale=message.locale,
        )

        await self.repository.create_in_app(
            notification_id=message.notification_id,
            organization_id=message.organization_id,
            recipient_user_id=recipient_uuid,
            type=message.template_id,
            title=title,
            body=body,
            payload=message.variables,
        )

        return NotificationResult(
            provider_reference=str(message.notification_id),
            accepted=True,
            status=NotificationStatus.DELIVERED,
        )

    async def list_in_app(
        self,
        recipient_user_id: UUID,
        *,
        organization_id: UUID | None = None,
        unread_only: bool = False,
    ) -> list[Any]:
        if not self.repository:
            return []
        return await self.repository.list_in_app_for_user(
            recipient_user_id,
            organization_id=organization_id,
            unread_only=unread_only,
        )

    async def mark_in_app_read(self, notification_id: UUID, recipient_user_id: UUID) -> bool:
        if not self.repository:
            return False
        return await self.repository.mark_as_read(notification_id, recipient_user_id)
