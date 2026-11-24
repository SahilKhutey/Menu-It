"""Restaurant module schemas for API transport (FCD-07 §9.1)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateRestaurantRequest(BaseModel):
    """Payload for creating a new restaurant location."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(..., min_length=2, max_length=160, description="Restaurant location name")
    slug: str = Field(..., min_length=2, max_length=80, description="URL-safe identifier")
    timezone: str = Field(default="UTC", max_length=64, description="IANA timezone name")

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
    """Payload for updating restaurant location details."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str | None = Field(default=None, min_length=2, max_length=160)
    timezone: str | None = Field(default=None, max_length=64)


class RestaurantSummaryResponse(BaseModel):
    """Summary representation of a restaurant."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    organization_id: UUID
    name: str
    slug: str
    timezone: str
    status: str
    created_at: datetime
    updated_at: datetime
