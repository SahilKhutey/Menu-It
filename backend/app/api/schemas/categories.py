"""
ModularMenu — Category API Schemas (ARC-07 §4.4).
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=180)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = Field(None, max_length=1000)
    sort_order: int = Field(default=0, ge=0)
    parent_category_id: UUID | None = None


class CategoryUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(None, min_length=1, max_length=180)
    description: str | None = Field(None, max_length=1000)
    sort_order: int | None = Field(None, ge=0)
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    menu_id: UUID
    parent_category_id: UUID | None = None
    name: str
    slug: str
    description: str | None = None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
