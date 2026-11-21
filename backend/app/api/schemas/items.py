"""
ModularMenu — Item & Pricing API Schemas (ARC-07 §4.4, §4.5).
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ItemPriceCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_name: str = Field(default="Regular", min_length=1, max_length=100)
    amount: Decimal = Field(ge=0, decimal_places=2)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    is_default: bool = True


class ItemPriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    menu_item_id: UUID
    price_name: str
    amount_minor: int
    amount: Decimal
    currency: str
    is_default: bool
    created_at: datetime


class ItemCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=180)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: Optional[str] = Field(None, max_length=2000)
    dietary_classification: str = Field(
        default="veg",
        pattern=r"^(veg|vegetarian|non_veg|egg|vegan|jain)$",
    )
    allergens: List[str] = Field(default_factory=list)
    is_available: bool = True
    sort_order: int = Field(default=0, ge=0)
    default_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    currency: str = Field(default="INR", min_length=3, max_length=3)


class ItemUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = Field(None, min_length=1, max_length=180)
    description: Optional[str] = Field(None, max_length=2000)
    dietary_classification: Optional[str] = Field(
        None, pattern=r"^(veg|vegetarian|non_veg|egg|vegan|jain)$"
    )
    allergens: Optional[List[str]] = None
    is_available: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)


class AvailabilityUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_available: bool


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: Optional[UUID] = None
    restaurant_id: UUID
    category_id: UUID
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    dietary_classification: Optional[str] = None
    dietary_type: Optional[str] = None
    allergens: List[str] = Field(default_factory=list)
    is_available: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def populate_dietary_and_slug(self) -> "ItemResponse":
        if not self.dietary_classification and self.dietary_type:
            self.dietary_classification = self.dietary_type
        if not self.slug and self.name:
            import re
            self.slug = re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")
        return self
