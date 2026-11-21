"""
ModularMenu — Menu API Schemas (ARC-07 §4.4).
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class MenuCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=180)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: Optional[str] = Field(None, max_length=2000)
    is_default: bool = False


class MenuUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = Field(None, min_length=1, max_length=180)
    description: Optional[str] = Field(None, max_length=2000)
    is_default: Optional[bool] = None
    status: Optional[str] = Field(None, pattern=r"^(draft|active|archived)$")


class MenuResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    status: str
    is_default: bool
    row_version: int
    created_at: datetime
    updated_at: datetime


class ReorderItem(BaseModel):
    id: UUID
    sort_order: int = Field(ge=0)


class ReorderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: List[ReorderItem]
