"""Email verification token database model (FCD-05 §10.1)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from menu_it.database.base import Base
from menu_it.database.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from menu_it.database.models.user import User


class EmailVerificationToken(
    UUIDPrimaryKeyMixin,
    Base,
):
    """Hashed token for asynchronous email address verification."""

    __tablename__ = "email_verification_tokens"
    __table_args__ = (
        UniqueConstraint(
            "token_hash",
            name="uq_email_verification_tokens_token_hash",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="verification_tokens",
    )
