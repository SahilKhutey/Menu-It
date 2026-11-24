"""User credential database model for secure password hash storage (FCD-05 §6.3)."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
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


class UserCredential(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Secure credential record isolating password hashes from profile operations."""

    __tablename__ = "user_credentials"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            name="uq_user_credentials_user_id",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="credential",
    )
