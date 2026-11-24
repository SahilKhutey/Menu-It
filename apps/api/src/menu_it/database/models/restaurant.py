"""Restaurant database model (FCD-03 §9.3)."""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
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
    from menu_it.database.models.tenant import Tenant


class RestaurantStatus(enum.StrEnum):
    """Lifecycle status of a restaurant."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"


class Restaurant(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Restaurant belonging to a tenant."""

    __tablename__ = "restaurants"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "slug",
            name="uq_restaurants_tenant_id_slug",
        ),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "tenants.id",
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

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="restaurants",
    )
