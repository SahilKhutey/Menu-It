"""Restaurant module schemas for API transport (FCD-07 §9.1, FCD-14 §7.2)."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateRestaurantRequest(BaseModel):
    """Payload for creating a new restaurant business unit."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(..., min_length=2, max_length=200, description="Restaurant name")
    slug: str = Field(..., min_length=2, max_length=100, description="URL-safe identifier")
    timezone: str = Field(default="UTC", max_length=100, description="IANA timezone name")
    description: str | None = Field(default=None, max_length=2000)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=30)
    website: str | None = Field(default=None, max_length=500)
    cuisine_type: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("Restaurant name cannot be empty.")
        return clean

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        clean = value.strip().lower()
        if not clean:
            raise ValueError("Restaurant slug cannot be empty.")
        if not all(char.isalnum() or char == "-" for char in clean):
            raise ValueError("Slug may contain only lowercase letters, numbers, and hyphens.")
        if clean.startswith("-") or clean.endswith("-"):
            raise ValueError("Slug cannot start or end with a hyphen.")
        return clean


class UpdateRestaurantRequest(BaseModel):
    """Payload for updating restaurant details."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str | None = Field(default=None, min_length=2, max_length=200)
    timezone: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=30)
    website: str | None = Field(default=None, max_length=500)
    cuisine_type: str | None = Field(default=None, max_length=100)


class RestaurantSummaryResponse(BaseModel):
    """Summary representation of a restaurant."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    slug: str
    timezone: str
    status: str
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    cuisine_type: str | None = None
    created_at: datetime
    updated_at: datetime


class RestaurantSettingsUpdateRequest(BaseModel):
    """Payload for updating restaurant settings."""

    model_config = ConfigDict(extra="forbid")

    settings_payload: dict[str, Any]


class RestaurantSettingsResponse(BaseModel):
    """Restaurant settings DTO."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    settings_payload: dict[str, Any]
    updated_at: datetime


class RestaurantMemberAssignRequest(BaseModel):
    """Payload for assigning a restaurant-scoped role."""

    model_config = ConfigDict(extra="forbid")

    role: str = Field(default="staff")


class RestaurantMemberResponse(BaseModel):
    """Restaurant membership DTO."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    user_id: UUID
    role: str
    created_at: datetime
    updated_at: datetime
