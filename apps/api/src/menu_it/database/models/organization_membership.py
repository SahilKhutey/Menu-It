"""Organization membership database model (FCD-04 §7.1, FCD-14 §5.5)."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from menu_it.database.base import Base
from menu_it.database.models.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from menu_it.database.models.organization import Organization
    from menu_it.database.models.user import User


class MembershipStatus(enum.StrEnum):
    """Lifecycle status of an organization membership."""

    INVITED = "invited"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class OrganizationRole(enum.StrEnum):
    """Role within an organization."""

    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"


class OrganizationMembership(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Membership linking an authenticated user to an organization."""

    __tablename__ = "organization_memberships"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_organization_membership_user",
        ),
        Index("ix_organization_memberships_user_id", "user_id"),
        Index("ix_organization_memberships_user_status", "user_id", "status"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[OrganizationRole] = mapped_column(
        Enum(OrganizationRole, name="organization_role", native_enum=False),
        nullable=False,
        default=OrganizationRole.STAFF,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus, name="membership_status", native_enum=False),
        nullable=False,
        default=MembershipStatus.ACTIVE,
    )
    joined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="memberships",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="organization_memberships",
        foreign_keys=[user_id],
    )
