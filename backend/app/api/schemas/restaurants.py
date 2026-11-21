"""
ModularMenu — Restaurant & Branch API Schemas (ARC-07 §4.3).
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class RestaurantCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=180)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: Optional[str] = None
    currency: str = Field(default="INR", min_length=3, max_length=3)
    time_zone: str = Field(default="Asia/Kolkata", min_length=1, max_length=64)


class RestaurantUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = Field(None, min_length=1, max_length=180)
    description: Optional[str] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    time_zone: Optional[str] = Field(None, min_length=1, max_length=64)


class RestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    status: str
    currency: str = "INR"
    time_zone: str = "Asia/Kolkata"
    created_at: datetime
    updated_at: datetime


class RestaurantSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    restaurant_id: UUID
    organization_id: UUID
    operating_hours: Dict[str, Any] = Field(default_factory=dict)
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None
    tax_identifier: Optional[str] = None
    table_count: int = 0
    fssai_license: Optional[str] = None


class RestaurantSettingsUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operating_hours: Optional[Dict[str, Any]] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None
    tax_identifier: Optional[str] = None
    table_count: Optional[int] = Field(None, ge=0)
    fssai_license: Optional[str] = None


class DesignConfigRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    theme_id: Optional[UUID] = None
    layout_preset: str = Field(default="grid", pattern=r"^(grid|list|cards|magazine|minimal)$")
    token_overrides: Dict[str, Any] = Field(default_factory=dict)
    component_visibility: Dict[str, bool] = Field(default_factory=dict)
    custom_css: Optional[str] = None


class DesignConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    restaurant_id: UUID
    organization_id: UUID
    theme_id: Optional[UUID] = None
    layout_preset: str
    token_overrides: Dict[str, Any]
    component_visibility: Dict[str, bool]
    custom_css: Optional[str] = None
    schema_version: int = 1
