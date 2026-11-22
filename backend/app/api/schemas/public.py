"""
ModularMenu — Public Menu Delivery Schemas (ARC-07 §4.11).
Strictly separates public consumption from internal tenant data.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PublicRestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    slug: str
    currency: str
    time_zone: str
    theme_preset: str | None = "minimal"
    theme_tokens: dict[str, Any] = {}
    fssai_license: str | None = None


class PublicMenuSummary(BaseModel):
    name: str
    slug: str
    description: str | None = None
    is_active: bool = True


class PublicMenuSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    restaurant_name: str
    restaurant_slug: str
    menu_name: str
    menu_slug: str
    version_number: int
    published_at: datetime
    sha256_digest: str
    theme_tokens: dict[str, Any]
    layout_preset: str
    categories: list[dict[str, Any]]
    items: list[dict[str, Any]]
