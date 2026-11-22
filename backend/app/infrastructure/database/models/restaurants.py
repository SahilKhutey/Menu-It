"""
ModularMenu — Restaurant & Branch Persistence Models (ARC-06 §3.2, §4.3).
Subordinate branch entity, branch member scoping, settings, and custom domain routing.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID, PortableJSON
from app.shared.infrastructure.database.base import Base, Timestamped, UUIDPrimaryKey


class RestaurantModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "restaurants"
    __table_args__ = (
        UniqueConstraint("organization_id", "id", name="uq_restaurants_org_id_id"),
        UniqueConstraint("organization_id", "slug", name="uq_restaurants_org_slug"),
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended')", name="ck_restaurants_status"
        ),
        CheckConstraint("length(default_currency) = 3", name="ck_restaurants_currency"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    timezone: Mapped[str] = mapped_column(String(80), default="UTC", nullable=False)
    default_currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)


class RestaurantMemberModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "restaurant_members"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "user_id", name="uq_restaurant_members_user"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_restaurant_members_restaurant",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(40), default="restaurant_manager", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)


class RestaurantSettingsModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "restaurant_settings"
    __table_args__ = (
        UniqueConstraint("organization_id", "restaurant_id", name="uq_restaurant_settings_rest"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_restaurant_settings_restaurant",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    settings: Mapped[dict[str, Any]] = mapped_column(PortableJSON(), default=dict, nullable=False)


class RestaurantDomainModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "restaurant_domains"
    __table_args__ = (
        UniqueConstraint("hostname", name="uq_restaurant_domain_hostname"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_restaurant_domains_restaurant",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    hostname: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
