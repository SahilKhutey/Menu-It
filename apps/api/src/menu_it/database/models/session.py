"""Session and refresh token database models (FCD-05 §9.1, §9.2)."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from menu_it.database.base import Base
from menu_it.database.models.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from menu_it.database.models.user import User


class SessionStatus(enum.StrEnum):
    """Lifecycle status of an authenticated user session."""

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class UserSession(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Authenticated user session tracking device metadata and server-side state."""

    __tablename__ = "user_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status", native_enum=False),
        default=SessionStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sessions",
    )
    refresh_tokens: Mapped[list["RefreshTokenRecord"]] = relationship(
        "RefreshTokenRecord",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class RefreshTokenRecord(
    UUIDPrimaryKeyMixin,
    Base,
):
    """Hashed refresh token record supporting rotation and reuse detection."""

    __tablename__ = "refresh_token_records"
    __table_args__ = (
        UniqueConstraint(
            "token_hash",
            name="uq_refresh_token_records_token_hash",
        ),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    family_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
        index=True,
    )
    is_consumed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    session: Mapped["UserSession"] = relationship(
        "UserSession",
        back_populates="refresh_tokens",
    )
