"""Restaurant database model (FCD-04 §6.1, §7.2)."""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from menu_it.database.base import Base
from menu_it.database.models.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from menu_it.database.models.organization import Organization
    from menu_it.database.models.restaurant_membership import RestaurantMembership


class RestaurantStatus(enum.StrEnum):
    """Lifecycle status of a restaurant location."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class Restaurant(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Subordinate restaurant location owned by an organization."""

    __tablename__ = "restaurants"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_restaurants_organization_id_slug",
        ),
        UniqueConstraint(
            "organization_id",
            "id",
            name="uq_restaurants_org_id",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="UTC",
    )
    status: Mapped[RestaurantStatus] = mapped_column(
        Enum(RestaurantStatus, name="restaurant_status", native_enum=False),
        default=RestaurantStatus.ACTIVE,
        nullable=False,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="restaurants",
    )
    memberships: Mapped[list["RestaurantMembership"]] = relationship(
        "RestaurantMembership",
        back_populates="restaurant",
        passive_deletes="all",
    )

    # Compatibility synonym for FCD-03 code referencing tenant_id
    tenant_id = synonym("organization_id")
