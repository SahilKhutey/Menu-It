"""Organization and restaurant settings database models (FCD-14 §5.1)."""

import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class OrganizationSettings(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Organization-level operational settings."""

    __tablename__ = "organization_settings"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    settings_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )


class RestaurantSettings(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Restaurant-level operational settings."""

    __tablename__ = "restaurant_settings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_restaurant_settings_org_restaurant",
            ondelete="CASCADE",
        ),
        UniqueConstraint("restaurant_id", name="uq_restaurant_settings_restaurant_id"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    settings_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
