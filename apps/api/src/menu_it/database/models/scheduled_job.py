"""SQLAlchemy models for persistent scheduled jobs and run history (FCD-10 WP-07)."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ScheduledJobModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Database representation of persistent schedule definitions."""

    __tablename__ = "scheduled_jobs"
    __table_args__ = (
        Index("ix_scheduled_jobs_organization_id", "organization_id"),
        Index("ix_scheduled_jobs_job_type", "job_type"),
        Index("ix_scheduled_jobs_next_run_at", "next_run_at"),
        Index("ix_scheduled_jobs_enabled", "enabled"),
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
        default=dict,
    )
    schedule_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,  # "cron", "interval", "once"
    )
    schedule_expression: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="UTC",
    )
    next_run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


class ScheduledJobRunModel(UUIDPrimaryKeyMixin, Base):
    """Durable occurrence execution history preventing duplicate scheduled job runs."""

    __tablename__ = "scheduled_job_runs"
    __table_args__ = (
        Index("ix_scheduled_job_runs_job_id", "scheduled_job_id"),
        Index("ix_scheduled_job_runs_run_key", "run_key", unique=True),
    )

    scheduled_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scheduled_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    run_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="completed",
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
