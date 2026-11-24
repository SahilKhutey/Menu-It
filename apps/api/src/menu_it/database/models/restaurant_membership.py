"""Restaurant membership database model (FCD-04 §7.2)."""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from menu_it.database.base import Base
from menu_it.database.models.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from menu_it.database.models.restaurant import Restaurant
    from menu_it.database.models.user import User


class RestaurantRole(enum.StrEnum):
    """Role within a specific restaurant."""

    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"


class RestaurantMembership(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Assignment linking an authenticated user to a specific restaurant."""

    __tablename__ = "restaurant_memberships"
    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "user_id",
            name="uq_restaurant_membership_user",
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_restaurant_membership_org_restaurant",
            ondelete="RESTRICT",
        ),
        Index("ix_restaurant_memberships_user_id", "user_id"),
        Index("ix_restaurant_memberships_org_id", "organization_id"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[RestaurantRole] = mapped_column(
        Enum(RestaurantRole, name="restaurant_role", native_enum=False),
        nullable=False,
        default=RestaurantRole.STAFF,
    )

    # Relationships
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="memberships",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="restaurant_memberships",
    )
