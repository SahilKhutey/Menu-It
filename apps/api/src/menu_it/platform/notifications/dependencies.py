"""FastAPI dependencies for platform notification services (FCD-09 WP-03)."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.core.config import get_settings
from menu_it.database.session import get_db_session
from menu_it.platform.audit.publisher import LoggingAuditEventPublisher
from menu_it.platform.notifications.application.renderer import TemplateRenderer
from menu_it.platform.notifications.application.service import NotificationService
from menu_it.platform.notifications.domain.contracts import NotificationChannel
from menu_it.platform.notifications.infrastructure.email_adapter import (
    ConsoleEmailProvider,
    EmailNotificationAdapter,
)
from menu_it.platform.notifications.infrastructure.repository import NotificationRepository


def get_notification_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> NotificationService:
    """Construct request-scoped NotificationService with configured adapters and repository."""
    get_settings()
    repo = NotificationRepository(session)
    renderer = TemplateRenderer()
    audit_pub = LoggingAuditEventPublisher()

    # Configure Email Adapter
    email_provider = ConsoleEmailProvider()
    email_adapter = EmailNotificationAdapter(provider=email_provider, renderer=renderer)

    adapters = {
        NotificationChannel.EMAIL: email_adapter,
    }

    return NotificationService(
        adapters=adapters,
        repository=repo,
        renderer=renderer,
        audit_publisher=audit_pub,
    )
