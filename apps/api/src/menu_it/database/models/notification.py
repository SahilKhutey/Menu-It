"""SQLAlchemy database models for in-app notifications and delivery tracking (FCD-09 WP-03)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import UUIDPrimaryKeyMixin


class NotificationModel(UUIDPrimaryKeyMixin, Base):
    """In-app notifications persisted for recipients."""

    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_org_id", "organization_id"),
        Index("ix_notifications_recipient_read", "recipient_user_id", "read_at"),
        Index("ix_notifications_created_at", "created_at"),
    )

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )
    recipient_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    payload: Mapped[Any | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class NotificationDeliveryModel(UUIDPrimaryKeyMixin, Base):
    """Delivery tracking record for outbound notifications across channels."""

    __tablename__ = "notification_deliveries"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_notification_deliveries_idempotency_key"),
        Index("ix_notification_deliveries_notification_id", "notification_id"),
        Index("ix_notification_deliveries_channel_status", "channel", "status"),
    )

    notification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
    )
    channel: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    provider_reference: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    error_code: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
