"""Database repository for file metadata (FCD-09 WP-02)."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.file import FileModel
from menu_it.platform.files.domain.models import FileMetadata, FileStatus, FileVisibility


class FileRepository:
    """Async repository managing FileModel persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _to_domain(model: FileModel) -> FileMetadata:
        return FileMetadata(
            id=model.id,
            organization_id=model.organization_id,
            uploaded_by=model.uploaded_by,
            original_filename=model.original_filename,
            storage_key=model.storage_key,
            mime_type=model.mime_type,
            size_bytes=model.size_bytes,
            checksum_sha256=model.checksum_sha256,
            visibility=FileVisibility(model.visibility),
            status=FileStatus(model.status),
            created_at=model.created_at,
            deleted_at=model.deleted_at,
        )

    async def save(self, metadata: FileMetadata) -> FileMetadata:
        """Insert or update file metadata record."""
        model = FileModel(
            id=metadata.id,
            organization_id=metadata.organization_id,
            uploaded_by=metadata.uploaded_by,
            original_filename=metadata.original_filename,
            storage_key=metadata.storage_key,
            mime_type=metadata.mime_type,
            size_bytes=metadata.size_bytes,
            checksum_sha256=metadata.checksum_sha256,
            visibility=str(metadata.visibility),
            status=str(metadata.status),
            created_at=metadata.created_at,
            deleted_at=metadata.deleted_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def get_by_id(self, file_id: UUID) -> FileMetadata | None:
        """Fetch file metadata by primary key, filtering out soft-deleted records."""
        stmt = select(FileModel).where(FileModel.id == file_id, FileModel.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_id_including_deleted(self, file_id: UUID) -> FileMetadata | None:
        """Fetch file metadata by primary key including deleted records."""
        stmt = select(FileModel).where(FileModel.id == file_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def soft_delete(self, file_id: UUID) -> bool:
        """Mark a file as deleted with current UTC timestamp."""
        stmt = (
            update(FileModel)
            .where(FileModel.id == file_id, FileModel.deleted_at.is_(None))
            .values(deleted_at=datetime.now(UTC), status=str(FileStatus.DELETED))
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
