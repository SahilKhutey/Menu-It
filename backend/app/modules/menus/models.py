import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator
from app.core.database import Base, GUID, TimestampMixin, PortableJSON


class Menu(Base, TimestampMixin):
    __tablename__ = "menus"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "slug", name="uq_restaurant_menu_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    menu_type: Mapped[str] = mapped_column(String(50), default="all_day", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="menus", lazy="raise")
    categories: Mapped[List["Category"]] = relationship(
        "Category", back_populates="menu", cascade="all, delete-orphan", lazy="raise"
    )
    versions: Mapped[List["MenuVersion"]] = relationship(
        "MenuVersion", back_populates="menu", cascade="all, delete-orphan", lazy="raise"
    )


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    menu_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("menus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    menu: Mapped["Menu"] = relationship("Menu", back_populates="categories", lazy="raise")
    items: Mapped[List["MenuItem"]] = relationship(
        "MenuItem", back_populates="category", cascade="all, delete-orphan", lazy="raise"
    )


class MenuItem(Base, TimestampMixin):
    __tablename__ = "menu_items"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    dietary_type: Mapped[str] = mapped_column(String(30), default="vegetarian", nullable=False)
    # veg, non_veg, egg, vegan, jain
    spice_level: Mapped[str] = mapped_column(String(20), default="none", nullable=False)
    # none, mild, medium, hot, extra_hot
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ingredients: Mapped[List[str]] = mapped_column(PortableJSON(), default=list, nullable=False)
    allergens: Mapped[List[str]] = mapped_column(PortableJSON(), default=list, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="items", lazy="raise")
    variants: Mapped[List["ItemVariant"]] = relationship(
        "ItemVariant", back_populates="menu_item", cascade="all, delete-orphan", lazy="raise"
    )
    item_addons: Mapped[List["ItemAddon"]] = relationship(
        "ItemAddon", back_populates="menu_item", cascade="all, delete-orphan", lazy="raise"
    )


class ItemVariant(Base):
    __tablename__ = "item_variants"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    menu_item_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_delta: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="variants", lazy="raise")


class Addon(Base):
    __tablename__ = "addons"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_delta: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ItemAddon(Base):
    __tablename__ = "item_addons"
    __table_args__ = (
        UniqueConstraint("menu_item_id", "addon_id", name="uq_item_addon"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    menu_item_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    addon_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("addons.id", ondelete="CASCADE"), nullable=False
    )
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="item_addons", lazy="raise")
    addon: Mapped["Addon"] = relationship("Addon", lazy="raise")


class MenuVersion(Base):
    __tablename__ = "menu_versions"
    __table_args__ = (
        UniqueConstraint("menu_id", "version_number", name="uq_menu_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    menu_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("menus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_data: Mapped[Dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    published_by: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id"), nullable=True)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    menu: Mapped["Menu"] = relationship("Menu", back_populates="versions", lazy="raise")


class Publication(Base):
    __tablename__ = "publications"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "menu_id", name="uq_active_publication"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    menu_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("menus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    active_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("menu_versions.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default="published", nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    active_version: Mapped["MenuVersion"] = relationship("MenuVersion", lazy="raise")
