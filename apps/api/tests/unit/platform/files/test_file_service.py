"""Unit tests for FileService orchestration and authorization (FCD-09 WP-02)."""

import io
from pathlib import Path
from uuid import uuid4

import pytest

from menu_it.platform.audit.publisher import InMemoryAuditEventPublisher
from menu_it.platform.files.application.service import (
    FileAccessDeniedError,
    FileNotFoundException,
    FileService,
)
from menu_it.platform.files.domain.models import FileMetadata, FileVisibility
from menu_it.platform.files.infrastructure.local_storage import LocalFileStorage

PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 30


class InMemoryFileRepository:
    """Mock in-memory repository for unit testing service logic."""

    def __init__(self) -> None:
        self.files: dict[str, FileMetadata] = {}

    async def save(self, metadata: FileMetadata) -> FileMetadata:
        self.files[str(metadata.id)] = metadata
        return metadata

    async def get_by_id(self, file_id) -> FileMetadata | None:
        file = self.files.get(str(file_id))
        if file and file.deleted_at is None:
            return file
        return None

    async def soft_delete(self, file_id) -> bool:
        file = self.files.get(str(file_id))
        if file and file.deleted_at is None:
            object.__setattr__(file, "deleted_at", "deleted")
            return True
        return False


@pytest.mark.asyncio
async def test_file_service_upload_and_authorization(tmp_path: Path):
    """Uploads file, tracks audit, and enforces tenant boundaries."""
    repo = InMemoryFileRepository()
    storage = LocalFileStorage(root=tmp_path)
    audit = InMemoryAuditEventPublisher()
    service = FileService(repository=repo, storage=storage, audit_publisher=audit)

    org_a = uuid4()
    org_b = uuid4()
    user_a = uuid4()

    # Upload tenant-private file
    meta = await service.upload(
        content=PNG_MAGIC,
        original_filename="logo.png",
        organization_id=org_a,
        uploaded_by=user_a,
        visibility=FileVisibility.TENANT_PRIVATE,
    )

    assert meta.original_filename == "logo.png"
    assert len(audit.events) == 1
    assert audit.events[0].event_type == "file.uploaded"

    # Tenant A access succeeds
    retrieved = await service.get_metadata(meta.id, current_org_id=org_a)
    assert retrieved.id == meta.id

    # Content stream succeeds
    _, stream = await service.get_content(meta.id, current_org_id=org_a)
    assert stream.read() == PNG_MAGIC

    # Tenant B access denied
    with pytest.raises(FileAccessDeniedError):
        await service.get_metadata(meta.id, current_org_id=org_b)

    with pytest.raises(FileAccessDeniedError):
        await service.get_content(meta.id, current_org_id=org_b)

    # Delete by authorized tenant
    await service.delete_file(meta.id, current_org_id=org_a, current_user_id=user_a)
    assert len(audit.events) == 2
    assert audit.events[1].event_type == "file.deleted"

    # Subsequent fetch raises 404
    with pytest.raises(FileNotFoundException):
        await service.get_metadata(meta.id, current_org_id=org_a)


@pytest.mark.asyncio
async def test_public_file_accessible_without_org(tmp_path: Path):
    """Public files can be accessed without organization context."""
    repo = InMemoryFileRepository()
    storage = LocalFileStorage(root=tmp_path)
    service = FileService(repository=repo, storage=storage)

    meta = await service.upload(
        content=PNG_MAGIC,
        original_filename="public-menu.png",
        organization_id=uuid4(),
        uploaded_by=uuid4(),
        visibility=FileVisibility.PUBLIC,
    )

    # Retrieved with None context
    retrieved = await service.get_metadata(meta.id, current_org_id=None)
    assert retrieved.id == meta.id
