"""
ModularMenu — Pricing, Variations & Localization Models (ARC-06 §3.2, §4.3).
Fixed-precision monetary representation (integer minor units / NUMERIC),
serving variants, add-ons, and multilingual translations.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID
from app.shared.infrastructure.database.base import Base, UUIDPrimaryKey


class ItemPriceModel(Base, UUIDPrimaryKey):
    __tablename__ = "item_prices"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "item_id"],
            ["menu_items.organization_id", "menu_items.restaurant_id", "menu_items.id"],
            name="fk_item_prices_item",
            ondelete="CASCADE",
        ),
        CheckConstraint("amount_minor >= 0", name="ck_item_prices_amount"),
        CheckConstraint("length(currency) = 3", name="ck_item_prices_currency"),
        Index(
            "uq_item_prices_one_default",
            "organization_id",
            "restaurant_id",
            "item_id",
            unique=True,
            sqlite_where=mapped_column("is_default").is_(True),
            postgresql_where="is_default = TRUE",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    item_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    price_label: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ItemVariantModel(Base, UUIDPrimaryKey):
    __tablename__ = "item_variants"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "item_id"],
            ["menu_items.organization_id", "menu_items.restaurant_id", "menu_items.id"],
            name="fk_item_variants_item",
            ondelete="CASCADE",
        ),
        CheckConstraint("amount_minor >= 0", name="ck_item_variants_amount"),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    item_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Half", "Full", "Large"
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class AddonModel(Base, UUIDPrimaryKey):
    __tablename__ = "addons"
    __table_args__ = (
        UniqueConstraint("organization_id", "restaurant_id", "id", name="uq_addons_org_restaurant_id"),
        CheckConstraint("amount_minor >= 0", name="ck_addons_amount"),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)


class ItemAddonModel(Base, UUIDPrimaryKey):
    __tablename__ = "item_addons"
    __table_args__ = (
        UniqueConstraint("item_id", "addon_id", name="uq_item_addon_pair"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "item_id"],
            ["menu_items.organization_id", "menu_items.restaurant_id", "menu_items.id"],
            name="fk_item_addons_item",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "addon_id"],
            ["addons.organization_id", "addons.restaurant_id", "addons.id"],
            name="fk_item_addons_addon",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    item_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    addon_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class MenuItemTranslationModel(Base, UUIDPrimaryKey):
    __tablename__ = "menu_item_translations"
    __table_args__ = (
        UniqueConstraint("item_id", "locale", name="uq_item_translation_locale"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "item_id"],
            ["menu_items.organization_id", "menu_items.restaurant_id", "menu_items.id"],
            name="fk_item_translations_item",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    item_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    locale: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g. "hi-IN", "mr-IN", "es-ES"
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
