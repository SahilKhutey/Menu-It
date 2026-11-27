"""File application service managing uploads, validation, and retrieval (FCD-09 WP-02)."""

import io
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO
from uuid import UUID, uuid4

from menu_it.platform.audit.contracts import AuditEvent, AuditEventPublisher
from menu_it.platform.files.application.storage_keys import build_storage_key
from menu_it.platform.files.application.validation import validate_file_content
from menu_it.platform.files.domain.models import FileMetadata, FileStatus, FileVisibility
from menu_it.platform.files.domain.storage import FileStorage
from menu_it.platform.files.infrastructure.repository import FileRepository


class FileAccessDeniedError(Exception):
    """Raised when an actor is not authorized to access or mutate a file."""


class FileNotFoundException(Exception):
    """Raised when the requested file does not exist or has been deleted."""


class FileService:
    """Orchestrates secure file upload, storage, authorization, and lifecycle."""

    def __init__(
        self,
        repository: FileRepository,
        storage: FileStorage,
        audit_publisher: AuditEventPublisher | None = None,
        max_upload_bytes: int = 10485760,
        allowed_mime_types: set[str] | None = None,
    ) -> None:
        self.repository = repository
        self.storage = storage
        self.audit_publisher = audit_publisher
        self.max_upload_bytes = max_upload_bytes
        self.allowed_mime_types = allowed_mime_types or {
            "image/jpeg",
            "image/png",
            "image/webp",
            "application/pdf",
        }

    async def upload(
        self,
        *,
        content: bytes,
        original_filename: str,
        organization_id: UUID | None,
        uploaded_by: UUID | None,
        visibility: FileVisibility = FileVisibility.TENANT_PRIVATE,
        correlation_id: str | None = None,
    ) -> FileMetadata:
        """Validate content, store in storage adapter, and persist metadata."""
        validated = validate_file_content(
            filename=original_filename,
            content=content,
            max_bytes=self.max_upload_bytes,
            allowed_mimes=self.allowed_mime_types,
        )

        file_id = uuid4()
        ext = Path(validated.filename).suffix.lower()
        storage_key = build_storage_key(
            organization_id=organization_id,
            file_id=file_id,
            extension=ext,
        )

        # Store object in storage adapter
        stream = io.BytesIO(content)
        stored_object = await self.storage.put(
            key=storage_key,
            content=stream,
            content_type=validated.content_type,
        )

        metadata = FileMetadata(
            id=file_id,
            organization_id=organization_id,
            uploaded_by=uploaded_by,
            original_filename=validated.filename,
            storage_key=stored_object.storage_key,
            mime_type=validated.content_type,
            size_bytes=stored_object.size_bytes,
            checksum_sha256=stored_object.checksum_sha256,
            visibility=visibility,
            status=FileStatus.STORED,
            created_at=datetime.now(UTC),
        )

        try:
            persisted = await self.repository.save(metadata)
        except Exception as exc:
            # Cleanup orphaned physical file on database failure
            await self.storage.delete(key=storage_key)
            raise exc

        if self.audit_publisher:
            await self.audit_publisher.publish(
                AuditEvent(
                    event_id=uuid4(),
                    event_type="file.uploaded",
                    occurred_at=datetime.now(UTC),
                    organization_id=organization_id,
                    actor_user_id=uploaded_by,
                    resource_type="file",
                    resource_id=str(file_id),
                    action="upload",
                    outcome="success",
                    correlation_id=correlation_id,
                    metadata={
                        "filename": validated.filename,
                        "size_bytes": stored_object.size_bytes,
                        "mime_type": validated.content_type,
                        "visibility": str(visibility),
                    },
                )
            )

        return persisted

    def check_authorization(
        self,
        metadata: FileMetadata,
        current_org_id: UUID | None,
        current_user_id: UUID | None,
        is_platform_admin: bool = False,
    ) -> None:
        """Enforce visibility and tenant boundaries."""
        if is_platform_admin:
            return

        if metadata.visibility == FileVisibility.PUBLIC:
            return

        if metadata.visibility == FileVisibility.TENANT_PRIVATE:
            if current_org_id is None or metadata.organization_id != current_org_id:
                raise FileAccessDeniedError("Access to tenant-private file is forbidden.")
            return

        if metadata.visibility == FileVisibility.USER_PRIVATE:
            if current_user_id is None or metadata.uploaded_by != current_user_id:
                raise FileAccessDeniedError("Access to user-private file is forbidden.")
            return

        if metadata.visibility == FileVisibility.PLATFORM_PRIVATE:
            raise FileAccessDeniedError(
                "Access to platform-private file requires platform administrative privileges."
            )

    async def get_metadata(
        self,
        file_id: UUID,
        current_org_id: UUID | None = None,
        current_user_id: UUID | None = None,
        is_platform_admin: bool = False,
    ) -> FileMetadata:
        """Retrieve authorized file metadata."""
        meta = await self.repository.get_by_id(file_id)
        if meta is None or meta.deleted_at is not None:
            raise FileNotFoundException(f"File '{file_id}' was not found or has been deleted.")

        self.check_authorization(
            meta,
            current_org_id=current_org_id,
            current_user_id=current_user_id,
            is_platform_admin=is_platform_admin,
        )
        return meta

    async def get_content(
        self,
        file_id: UUID,
        current_org_id: UUID | None = None,
        current_user_id: UUID | None = None,
        is_platform_admin: bool = False,
    ) -> tuple[FileMetadata, BinaryIO]:
        """Retrieve authorized file binary stream."""
        meta = await self.get_metadata(
            file_id=file_id,
            current_org_id=current_org_id,
            current_user_id=current_user_id,
            is_platform_admin=is_platform_admin,
        )
        stream = await self.storage.open(key=meta.storage_key)
        return meta, stream

    async def delete_file(
        self,
        file_id: UUID,
        current_org_id: UUID | None = None,
        current_user_id: UUID | None = None,
        is_platform_admin: bool = False,
        correlation_id: str | None = None,
    ) -> None:
        """Authorize and soft-delete a file."""
        meta = await self.repository.get_by_id(file_id)
        if meta is None:
            raise FileNotFoundException(f"File '{file_id}' was not found.")

        self.check_authorization(
            meta,
            current_org_id=current_org_id,
            current_user_id=current_user_id,
            is_platform_admin=is_platform_admin,
        )

        await self.repository.soft_delete(file_id)

        if self.audit_publisher:
            await self.audit_publisher.publish(
                AuditEvent(
                    event_id=uuid4(),
                    event_type="file.deleted",
                    occurred_at=datetime.now(UTC),
                    organization_id=meta.organization_id,
                    actor_user_id=current_user_id,
                    resource_type="file",
                    resource_id=str(file_id),
                    action="delete",
                    outcome="success",
                    correlation_id=correlation_id,
                    metadata={"filename": meta.original_filename},
                )
            )
