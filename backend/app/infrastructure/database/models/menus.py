"""
ModularMenu — Menu Domain Persistence Models (ARC-06 §3.2, §4.3).
Menus, hierarchical categories, and food items with database-enforced composite ownership chains:
organization -> restaurant -> menu -> category -> item.
"""

from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID
from app.shared.infrastructure.database.base import Base, Timestamped, UUIDPrimaryKey


class MenuModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "menus"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "restaurant_id", "id", name="uq_menus_org_restaurant_id"
        ),
        UniqueConstraint(
            "organization_id", "restaurant_id", "slug", name="uq_menus_restaurant_slug"
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_menus_restaurant",
            ondelete="CASCADE",
        ),
        CheckConstraint("status IN ('draft', 'active', 'archived')", name="ck_menus_status"),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    row_version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )  # Optimistic concurrency (ARC06 §10.2)


class MenuCategoryModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "menu_categories"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "restaurant_id",
            "menu_id",
            "id",
            name="uq_categories_org_restaurant_menu_id",
        ),
        UniqueConstraint(
            "organization_id", "restaurant_id", "id", name="uq_categories_org_restaurant_id"
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "menu_id"],
            ["menus.organization_id", "menus.restaurant_id", "menus.id"],
            name="fk_categories_menu",
            ondelete="CASCADE",
        ),
        CheckConstraint("sort_order >= 0", name="ck_categories_sort_order"),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    menu_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class MenuItemModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "menu_items"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "restaurant_id", "id", name="uq_items_org_restaurant_id"
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "category_id"],
            [
                "menu_categories.organization_id",
                "menu_categories.restaurant_id",
                "menu_categories.id",
            ],
            name="fk_items_category",
            ondelete="CASCADE",
        ),
        CheckConstraint("status IN ('active', 'inactive', 'archived')", name="ck_items_status"),
        CheckConstraint("sort_order >= 0", name="ck_items_sort_order"),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    category_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
