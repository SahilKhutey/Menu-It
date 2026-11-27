"""Restaurant business profile database model (FCD-06 §14.1)."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from menu_it.database.base import Base
from menu_it.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from menu_it.database.models.organization import Organization
    from menu_it.database.models.restaurant import Restaurant


class RestaurantProfileRecord(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Database record for restaurant business profiles with composite tenant foreign key."""

    __tablename__ = "restaurant_profiles"
    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            name="uq_restaurant_profiles_restaurant_id",
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_restaurant_profiles_org_restaurant",
            ondelete="CASCADE",
        ),
        Index(
            "ix_restaurant_profiles_organization_id",
            "organization_id",
        ),
        Index(
            "ix_restaurant_profiles_restaurant_id",
            "restaurant_id",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
    )
    public_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    legal_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )
    address_line_1: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    address_line_2: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    address_locality: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    address_admin_area: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    address_postal_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    address_country_code: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
    )
    primary_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )
    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="UTC",
    )
    schedule_payload: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    website_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )
    logo_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    banner_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    short_description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cuisine_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price_range: Mapped[str | None] = mapped_column(String(20), nullable=True)
    public_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    public_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    social_links: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        foreign_keys=[restaurant_id],
    )
