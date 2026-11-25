"""ARQ worker configuration and lifecycle management (FCD-10 WP-03)."""

from arq.connections import RedisSettings

from menu_it.core.config import get_settings
from menu_it.platform.jobs.registry import JOB_REGISTRY, register_job_type
from menu_it.platform.jobs.tasks import (
    process_file,
    rebuild_menu,
    send_notification,
)

# Register default core task handlers
register_job_type("notification.send", send_notification)
register_job_type("file.process", process_file)
register_job_type("menu.rebuild", rebuild_menu)


class WorkerSettings:
    """ARQ Worker configuration settings."""

    _settings = get_settings()

    redis_settings = RedisSettings.from_dsn(_settings.redis_url)
    functions = list(JOB_REGISTRY.values())
    max_jobs = _settings.worker_max_jobs
    job_timeout = _settings.worker_job_timeout
    max_tries = _settings.worker_max_tries
    keep_result = 3600
    queue_name = "menu-it:jobs:default"

    @classmethod
    async def on_startup(cls, ctx: dict) -> None:
        """Initialize worker platform services and database connection pools."""
        from menu_it.platform.container import build_platform_services
        ctx["services"] = build_platform_services()

    @classmethod
    async def on_shutdown(cls, ctx: dict) -> None:
        """Clean up worker platform resources."""
        pass
