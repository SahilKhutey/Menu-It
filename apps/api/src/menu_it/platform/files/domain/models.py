"""File domain models and lifecycle states (FCD-09 WP-02)."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class FileVisibility(StrEnum):
    """Access classification and privacy boundary for a stored file."""

    PUBLIC = "public"
    TENANT_PRIVATE = "tenant_private"
    USER_PRIVATE = "user_private"
    PLATFORM_PRIVATE = "platform_private"


class FileStatus(StrEnum):
    """Lifecycle status of a file within the platform."""

    PENDING = "pending"
    STORED = "stored"
    REJECTED = "rejected"
    FAILED = "failed"
    DELETED = "deleted"


@dataclass(frozen=True)
class FileMetadata:
    """Domain representation of file metadata."""

    id: UUID
    organization_id: UUID | None
    uploaded_by: UUID | None
    original_filename: str
    storage_key: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    visibility: FileVisibility
    status: FileStatus
    created_at: datetime
    deleted_at: datetime | None = None
