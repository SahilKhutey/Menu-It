"""
ModularMenu — Restaurant & Branch API Schemas (ARC-07 §4.3).
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RestaurantCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=180)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = None
    currency: str = Field(default="INR", min_length=3, max_length=3)
    time_zone: str = Field(default="Asia/Kolkata", min_length=1, max_length=64)


class RestaurantUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(None, min_length=1, max_length=180)
    description: str | None = None
    currency: str | None = Field(None, min_length=3, max_length=3)
    time_zone: str | None = Field(None, min_length=1, max_length=64)


class RestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    description: str | None = None
    status: str
    currency: str = "INR"
    time_zone: str = "Asia/Kolkata"
    created_at: datetime
    updated_at: datetime


class RestaurantSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    restaurant_id: UUID
    organization_id: UUID
    operating_hours: dict[str, Any] = Field(default_factory=dict)
    contact_phone: str | None = None
    contact_email: str | None = None
    address: str | None = None
    tax_identifier: str | None = None
    table_count: int = 0
    fssai_license: str | None = None


class RestaurantSettingsUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operating_hours: dict[str, Any] | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    address: str | None = None
    tax_identifier: str | None = None
    table_count: int | None = Field(None, ge=0)
    fssai_license: str | None = None


class DesignConfigRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    theme_id: UUID | None = None
    layout_preset: str = Field(default="grid", pattern=r"^(grid|list|cards|magazine|minimal)$")
    token_overrides: dict[str, Any] = Field(default_factory=dict)
    component_visibility: dict[str, bool] = Field(default_factory=dict)
    custom_css: str | None = None


class DesignConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    restaurant_id: UUID
    organization_id: UUID
    theme_id: UUID | None = None
    layout_preset: str
    token_overrides: dict[str, Any]
    component_visibility: dict[str, bool]
    custom_css: str | None = None
    schema_version: int = 1
