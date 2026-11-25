"""Platform service composition root and dependency container (FCD-09 WP-07)."""

from dataclasses import dataclass

from menu_it.core.config import Settings, get_settings
from menu_it.platform.audit.contracts import AuditEventPublisher
from menu_it.platform.audit.publisher import LoggingAuditEventPublisher
from menu_it.platform.common.clock import Clock, SystemClock
from menu_it.platform.files.domain.storage import FileStorage
from menu_it.platform.files.infrastructure.local_storage import LocalFileStorage
from menu_it.platform.notifications.application.renderer import TemplateRenderer
from menu_it.platform.notifications.application.service import NotificationService
from menu_it.platform.notifications.domain.contracts import NotificationChannel
from menu_it.platform.notifications.infrastructure.email_adapter import (
    ConsoleEmailProvider,
    EmailNotificationAdapter,
)


@dataclass(frozen=True)
class PlatformServices:
    """Singleton platform services composition container."""

    settings: Settings
    clock: Clock
    file_storage: FileStorage
    notification_service: NotificationService
    audit_publisher: AuditEventPublisher


def build_platform_services(settings: Settings | None = None) -> PlatformServices:
    """Construct platform service adapters and register dependencies."""
    cfg = settings or get_settings()
    clock = SystemClock()
    audit_pub = LoggingAuditEventPublisher()

    # File Storage
    storage = LocalFileStorage(root=cfg.file_storage_root)

    # Notifications
    email_provider = ConsoleEmailProvider()
    renderer = TemplateRenderer()
    email_adapter = EmailNotificationAdapter(provider=email_provider, renderer=renderer)
    adapters = {NotificationChannel.EMAIL: email_adapter}
    notification_service = NotificationService(
        adapters=adapters,
        renderer=renderer,
        audit_publisher=audit_pub,
    )

    return PlatformServices(
        settings=cfg,
        clock=clock,
        file_storage=storage,
        notification_service=notification_service,
        audit_publisher=audit_pub,
    )
