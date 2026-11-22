import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# Item Variant & Addon Schemas
class ItemVariantBase(BaseModel):
    name: str
    price_delta: Decimal = Decimal("0.00")
    is_available: bool = True
    sort_order: int = 0


class ItemVariantCreate(ItemVariantBase):
    pass


class ItemVariantOut(ItemVariantBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    menu_item_id: uuid.UUID


class AddonBase(BaseModel):
    name: str
    price_delta: Decimal = Decimal("0.00")
    is_available: bool = True


class AddonOut(AddonBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


# Food Item Schemas
DietaryType = Literal["vegetarian", "non_veg", "egg", "vegan", "jain"]
SpiceLevel = Literal["none", "mild", "medium", "hot", "extra_hot"]


class MenuItemBase(BaseModel):
    name: str
    description: str | None = None
    base_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency_code: str = "INR"
    dietary_type: DietaryType = "vegetarian"
    spice_level: SpiceLevel = "none"
    image_url: str | None = None
    ingredients: list[str] = []
    allergens: list[str] = []
    is_available: bool = True
    is_featured: bool = False
    sort_order: int = 0


class MenuItemCreate(MenuItemBase):
    variants: list[ItemVariantCreate] = []


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    base_price: float | None = None
    dietary_type: DietaryType | None = None
    spice_level: SpiceLevel | None = None
    image_url: str | None = None
    ingredients: list[str] | None = None
    allergens: list[str] | None = None
    is_available: bool | None = None
    is_featured: bool | None = None
    sort_order: int | None = None


class MenuItemOut(MenuItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    variants: list[ItemVariantOut] = []


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    slug: str | None = None
    description: str | None = None
    image_url: str | None = None
    sort_order: int = 0
    display_order: int | None = None
    is_visible: bool = True
    parent_id: uuid.UUID | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    image_url: str | None = None
    sort_order: int | None = None
    is_visible: bool | None = None


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    menu_id: uuid.UUID
    items: list[MenuItemOut] = []


# Menu Schemas
class MenuBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    menu_type: str = "all_day"
    status: str = "active"
    sort_order: int = 0


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    menu_type: str | None = None
    status: str | None = None
    sort_order: int | None = None


class MenuOut(MenuBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    restaurant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Publishing & Snapshot Schemas
class PublishedMenuSnapshot(BaseModel):
    restaurant: dict[str, Any]
    menu: dict[str, Any]
    categories: list[dict[str, Any]]
    theme: dict[str, Any]
    layout: dict[str, Any]
    published_at: str
    version_number: int
    checksum: str
