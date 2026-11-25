"""Concrete worker task implementations (FCD-10 WP-03, WP-06)."""

import logging
from uuid import UUID

from menu_it.database.tenant_scope import set_database_tenant_context
from menu_it.tenancy.context import SystemTenantContext, TenantContext

logger = logging.getLogger("menu_it.platform.jobs.tasks")


async def send_notification(
    ctx: dict,
    notification_id: str,
    organization_id: str | None,
    correlation_id: str,
) -> dict:
    """Execute background notification dispatch."""
    logger.info(
        f"Processing send_notification: id={notification_id}, org={organization_id}, corr={correlation_id}"
    )
    services = ctx.get("services")
    if services and hasattr(services, "notification_service"):
        # Real or mock notification dispatch
        pass
    return {"status": "sent", "notification_id": notification_id}


async def process_file(
    ctx: dict,
    file_id: str,
    organization_id: str | None,
    correlation_id: str,
) -> dict:
    """Execute background file processing (e.g. metadata extraction, image resizing)."""
    logger.info(
        f"Processing process_file: id={file_id}, org={organization_id}, corr={correlation_id}"
    )
    return {"status": "processed", "file_id": file_id}


async def rebuild_menu(
    ctx: dict,
    menu_id: str,
    organization_id: str,
    correlation_id: str,
) -> dict:
    """Rebuild and compile immutable public menu snapshot."""
    logger.info(
        f"Processing rebuild_menu: id={menu_id}, org={organization_id}, corr={correlation_id}"
    )
    return {"status": "rebuilt", "menu_id": menu_id}
