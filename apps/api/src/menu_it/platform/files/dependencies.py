"""FastAPI dependencies for platform file services (FCD-09 WP-02)."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.core.config import get_settings
from menu_it.database.session import get_db_session
from menu_it.platform.audit.publisher import LoggingAuditEventPublisher
from menu_it.platform.files.application.service import FileService
from menu_it.platform.files.infrastructure.local_storage import LocalFileStorage
from menu_it.platform.files.infrastructure.repository import FileRepository


def get_file_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FileService:
    """Construct request-scoped FileService backed by active db session and storage root."""
    settings = get_settings()
    repo = FileRepository(session)
    storage = LocalFileStorage(root=settings.file_storage_root)
    audit_pub = LoggingAuditEventPublisher()
    return FileService(
        repository=repo,
        storage=storage,
        audit_publisher=audit_pub,
        max_upload_bytes=settings.file_max_upload_bytes,
        allowed_mime_types=settings.file_allowed_mime_types,
    )
