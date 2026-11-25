"""SQLAlchemy database model for file metadata (FCD-09 WP-02)."""

from datetime import datetime
import uuid

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import UUIDPrimaryKeyMixin


class FileModel(UUIDPrimaryKeyMixin, Base):
    """Database representation of stored file metadata."""

    __tablename__ = "files"
    __table_args__ = (
        Index("ix_files_organization_id", "organization_id"),
        Index("ix_files_status", "status"),
        Index("ix_files_visibility", "visibility"),
        Index("ix_files_created_at", "created_at"),
    )

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    original_filename: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
    )
    storage_key: Mapped[str] = mapped_column(
        String(512),
        unique=True,
        nullable=False,
        index=True,
    )
    mime_type: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )
    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    checksum_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    visibility: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="tenant_private",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="stored",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
