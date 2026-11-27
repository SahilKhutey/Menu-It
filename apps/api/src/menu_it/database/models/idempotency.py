"""Idempotency record database model (FCD-07 WP-11)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import UUIDPrimaryKeyMixin


class IdempotencyRecord(UUIDPrimaryKeyMixin, Base):
    """Database record storing processed idempotent request signatures and responses."""

    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "actor_id",
            "key",
            name="uq_idempotency_org_actor_key",
        ),
        Index(
            "ix_idempotency_records_org_key",
            "organization_id",
            "key",
        ),
        Index(
            "ix_idempotency_records_expires_at",
            "expires_at",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )
    request_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    response_status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    response_body: Mapped[Any | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
