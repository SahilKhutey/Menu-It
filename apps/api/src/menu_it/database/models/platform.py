"""Platform membership database model for platform-level privileges (FCD-05 §16.1)."""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
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


class PlatformRole(enum.StrEnum):
    """Platform-level administrative and support roles."""

    PLATFORM_ADMIN = "platform_admin"
    PLATFORM_SUPPORT = "platform_support"
    PLATFORM_OPERATOR = "platform_operator"


class PlatformMembershipStatus(enum.StrEnum):
    """Lifecycle status of a platform-level membership."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class PlatformMembership(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Membership record granting platform-level privileges separated from tenant access."""

    __tablename__ = "platform_memberships"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            name="uq_platform_memberships_user_id",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[PlatformRole] = mapped_column(
        Enum(PlatformRole, name="platform_role", native_enum=False),
        nullable=False,
    )
    status: Mapped[PlatformMembershipStatus] = mapped_column(
        Enum(PlatformMembershipStatus, name="platform_membership_status", native_enum=False),
        default=PlatformMembershipStatus.ACTIVE,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="platform_membership",
    )
