"""SQLAlchemy model for transactional event outbox (FCD-10 WP-05)."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import UUIDPrimaryKeyMixin


class EventOutboxModel(UUIDPrimaryKeyMixin, Base):
    """Database representation of the transactional event outbox."""

    __tablename__ = "event_outbox"
    __table_args__ = (
        Index("ix_event_outbox_event_id", "event_id", unique=True),
        Index("ix_event_outbox_organization_id", "organization_id"),
        Index("ix_event_outbox_event_type", "event_type"),
        Index("ix_event_outbox_published_at", "published_at"),
        Index("ix_event_outbox_next_attempt_at", "next_attempt_at"),
        Index("ix_event_outbox_occurred_at", "occurred_at"),
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    schema_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    correlation_id: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    payload: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    locked_by: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
