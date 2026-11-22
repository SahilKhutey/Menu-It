"""
ModularMenu — Media Metadata Models (ARC-06 §3.2, §16 WP-ARC06-07).
Stores metadata for uploaded objects; actual bytes reside in tenant-isolated object storage.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID
from app.shared.infrastructure.database.base import Base, UUIDPrimaryKey


class MediaAssetModel(Base, UUIDPrimaryKey):
    __tablename__ = "media_assets"
    __table_args__ = (UniqueConstraint("object_key", name="uq_media_assets_key"),)

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID | None] = mapped_column(GUID(), nullable=True, index=True)
    object_key: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="available", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class MediaUsageModel(Base, UUIDPrimaryKey):
    __tablename__ = "media_usages"

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    media_asset_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("media_assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resource_type: Mapped[str] = mapped_column(
        String(80), nullable=False
    )  # 'menu_item', 'restaurant_logo', 'banner'
    resource_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
