import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional
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
    description: Optional[str] = None
    base_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency_code: str = "INR"
    dietary_type: DietaryType = "vegetarian"
    spice_level: SpiceLevel = "none"
    image_url: Optional[str] = None
    ingredients: List[str] = []
    allergens: List[str] = []
    is_available: bool = True
    is_featured: bool = False
    sort_order: int = 0


class MenuItemCreate(MenuItemBase):
    variants: List[ItemVariantCreate] = []


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    dietary_type: Optional[DietaryType] = None
    spice_level: Optional[SpiceLevel] = None
    image_url: Optional[str] = None
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    is_available: Optional[bool] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None


class MenuItemOut(MenuItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    variants: List[ItemVariantOut] = []


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    display_order: Optional[int] = None
    is_visible: bool = True
    parent_id: Optional[uuid.UUID] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_visible: Optional[bool] = None


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    menu_id: uuid.UUID
    items: List[MenuItemOut] = []


# Menu Schemas
class MenuBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    menu_type: str = "all_day"
    status: str = "active"
    sort_order: int = 0


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    menu_type: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None


class MenuOut(MenuBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    restaurant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Publishing & Snapshot Schemas
class PublishedMenuSnapshot(BaseModel):
    restaurant: Dict[str, Any]
    menu: Dict[str, Any]
    categories: List[Dict[str, Any]]
    theme: Dict[str, Any]
    layout: Dict[str, Any]
    published_at: str
    version_number: int
    checksum: str
