"""Durable security audit event database model (FCD-11 WP-07)."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import UUIDPrimaryKeyMixin


class SecurityAuditEventModel(
    UUIDPrimaryKeyMixin,
    Base,
):
    """Append-only security audit log for security events and auth operations."""

    __tablename__ = "security_audit_events"
    __table_args__ = (
        Index("ix_security_audit_events_occurred_at", "occurred_at"),
        Index("ix_security_audit_events_org_occurred", "organization_id", "occurred_at"),
        Index("ix_security_audit_events_actor_user", "actor_user_id"),
        Index("ix_security_audit_events_event_type", "event_type"),
        Index("ix_security_audit_events_outcome", "outcome"),
        Index("ix_security_audit_events_correlation", "correlation_id"),
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    outcome: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user",
        server_default="user",
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )
    restaurant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="SET NULL"),
        nullable=True,
    )
    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    resource_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    source_ip: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    reason_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
        server_default="{}",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
