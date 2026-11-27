"""SQLAlchemy model for background job status and execution metadata (FCD-10 WP-03)."""

import uuid

from sqlalchemy import JSON, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BackgroundJobModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Database representation of tracked background jobs."""

    __tablename__ = "background_jobs"
    __table_args__ = (
        Index("ix_background_jobs_organization_id", "organization_id"),
        Index("ix_background_jobs_status", "status"),
        Index("ix_background_jobs_job_type", "job_type"),
        Index("ix_background_jobs_idempotency_key", "idempotency_key", unique=True),
    )

    job_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
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
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="queued",
    )
    payload: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    max_tries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
