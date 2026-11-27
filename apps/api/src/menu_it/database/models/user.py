"""User database model representing independent identity accounts (FCD-05 §5.1)."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Integer,
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
    from menu_it.database.models.credential import UserCredential
    from menu_it.database.models.organization_membership import OrganizationMembership
    from menu_it.database.models.platform import PlatformMembership
    from menu_it.database.models.recovery import PasswordResetToken
    from menu_it.database.models.restaurant_membership import RestaurantMembership
    from menu_it.database.models.session import UserSession
    from menu_it.database.models.verification import EmailVerificationToken


class UserStatus(enum.StrEnum):
    """Lifecycle status of a user identity account."""

    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


def normalize_email(email: str) -> str:
    """Normalize email address to standard format."""
    normalized = email.strip().casefold()
    if not normalized:
        raise ValueError("Email is required.")
    return normalized


class User(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Core user account representing a person independent of organization memberships."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint(
            "normalized_email",
            name="uq_users_normalized_email",
        ),
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )
    normalized_email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status", native_enum=False),
        default=UserStatus.PENDING_VERIFICATION,
        nullable=False,
        index=True,
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    credential: Mapped["UserCredential | None"] = relationship(
        "UserCredential",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    organization_memberships: Mapped[list["OrganizationMembership"]] = relationship(
        "OrganizationMembership",
        back_populates="user",
        foreign_keys="[OrganizationMembership.user_id]",
        cascade="all, delete-orphan",
    )
    restaurant_memberships: Mapped[list["RestaurantMembership"]] = relationship(
        "RestaurantMembership",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    platform_membership: Mapped["PlatformMembership | None"] = relationship(
        "PlatformMembership",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
