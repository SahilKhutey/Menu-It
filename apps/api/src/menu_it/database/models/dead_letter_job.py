"""SQLAlchemy model for dead-letter background job failures (FCD-10 WP-04)."""

from datetime import datetime
import uuid

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import UUIDPrimaryKeyMixin


class DeadLetterJobModel(UUIDPrimaryKeyMixin, Base):
    """Database representation of permanently failed or exhausted background jobs."""

    __tablename__ = "dead_letter_jobs"
    __table_args__ = (
        Index("ix_dead_letter_jobs_organization_id", "organization_id"),
        Index("ix_dead_letter_jobs_job_id", "job_id"),
        Index("ix_dead_letter_jobs_job_type", "job_type"),
        Index("ix_dead_letter_jobs_dead_lettered_at", "dead_lettered_at"),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )
    job_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    payload: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    failure_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    failure_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    first_failed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    dead_lettered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    correlation_id: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    replayed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    replayed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
