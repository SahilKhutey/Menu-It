"""Security tests for platform services boundaries (FCD-09 WP-09)."""

import io
from pathlib import Path
from uuid import uuid4

import pytest

from menu_it.platform.files.application.service import FileAccessDeniedError, FileService
from menu_it.platform.files.application.validation import FileValidationError, validate_file_content
from menu_it.platform.files.domain.models import FileMetadata, FileVisibility
from menu_it.platform.files.infrastructure.local_storage import LocalFileStorage

PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 30


class InMemoryFileRepo:
    def __init__(self):
        self.db = {}

    async def save(self, m):
        self.db[str(m.id)] = m
        return m

    async def get_by_id(self, f_id):
        return self.db.get(str(f_id))

    async def soft_delete(self, f_id):
        if str(f_id) in self.db:
            object.__setattr__(self.db[str(f_id)], "deleted_at", "deleted")
            return True
        return False


@pytest.mark.asyncio
async def test_tenant_isolation_boundary_enforced(tmp_path: Path):
    """Tenant A cannot retrieve or delete Tenant B's files."""
    repo = InMemoryFileRepo()
    storage = LocalFileStorage(root=tmp_path)
    service = FileService(repository=repo, storage=storage)

    org_a = uuid4()
    org_b = uuid4()
    user_a = uuid4()
    user_b = uuid4()

    file_a = await service.upload(
        content=PNG_MAGIC,
        original_filename="private_doc.png",
        organization_id=org_a,
        uploaded_by=user_a,
        visibility=FileVisibility.TENANT_PRIVATE,
    )

    # Tenant B attempt to get metadata
    with pytest.raises(FileAccessDeniedError):
        await service.get_metadata(file_a.id, current_org_id=org_b, current_user_id=user_b)

    # Tenant B attempt to delete
    with pytest.raises(FileAccessDeniedError):
        await service.delete_file(file_a.id, current_org_id=org_b, current_user_id=user_b)


def test_malicious_path_traversal_filenames_blocked():
    """Path traversal filename attempts are blocked or sanitized."""
    with pytest.raises(FileValidationError):
        validate_file_content("", PNG_MAGIC, 100000, {"image/png"})

    res = validate_file_content("../../../logo.png", PNG_MAGIC, 100000, {"image/png"})
    assert res.filename == "logo.png"


@pytest.mark.asyncio
async def test_platform_private_file_requires_admin(tmp_path: Path):
    """Platform private files deny standard tenant access."""
    repo = InMemoryFileRepo()
    storage = LocalFileStorage(root=tmp_path)
    service = FileService(repository=repo, storage=storage)

    file_meta = await service.upload(
        content=PNG_MAGIC,
        original_filename="platform_report.png",
        organization_id=None,
        uploaded_by=None,
        visibility=FileVisibility.PLATFORM_PRIVATE,
    )

    with pytest.raises(FileAccessDeniedError):
        await service.get_metadata(file_meta.id, is_platform_admin=False)

    # Platform admin access succeeds
    meta = await service.get_metadata(file_meta.id, is_platform_admin=True)
    assert meta.id == file_meta.id
