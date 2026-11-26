"""Platform service composition root and dependency container (FCD-09 WP-07)."""

from dataclasses import dataclass

from menu_it.core.config import Settings, get_settings
from menu_it.platform.audit.contracts import AuditEventPublisher
from menu_it.platform.audit.publisher import LoggingAuditEventPublisher
from menu_it.platform.cache.contracts import InMemoryCacheBackend
from menu_it.platform.cache.service import CacheService
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
from menu_it.platform.security.rate_limit import InMemoryRateLimiter, RateLimiter, RedisRateLimiter


@dataclass(frozen=True)
class PlatformServices:
    """Singleton platform services composition container."""

    settings: Settings
    clock: Clock
    file_storage: FileStorage
    notification_service: NotificationService
    audit_publisher: AuditEventPublisher
    cache_service: CacheService
    rate_limiter: RateLimiter


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

    # Caching
    try:
        from menu_it.infrastructure.redis.cache_backend import RedisCacheBackend
        from menu_it.infrastructure.redis.client import create_redis_client

        redis_client = create_redis_client(settings=cfg)
        cache_backend = RedisCacheBackend(redis_client)
    except Exception:
        cache_backend = InMemoryCacheBackend()

    cache_service = CacheService(backend=cache_backend, enabled=cfg.cache_enabled)

    # Rate Limiting (FCD-11 WP-06)
    try:
        from menu_it.infrastructure.redis.client import create_redis_client

        redis_client = create_redis_client(settings=cfg)
        rate_limiter: RateLimiter = RedisRateLimiter(redis_client=redis_client)
    except Exception:
        rate_limiter = InMemoryRateLimiter()

    return PlatformServices(
        settings=cfg,
        clock=clock,
        file_storage=storage,
        notification_service=notification_service,
        audit_publisher=audit_pub,
        cache_service=cache_service,
        rate_limiter=rate_limiter,
    )
