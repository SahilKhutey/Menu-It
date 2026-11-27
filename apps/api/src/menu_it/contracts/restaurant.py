"""Restaurant API transport contracts (FCD-06 §12.5)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from menu_it.contracts.common import AddressDTO


class TimeRangeDTO(BaseModel):
    """Time range in HH:MM format."""

    model_config = ConfigDict(frozen=True)

    opens_at: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Opening time in HH:MM")
    closes_at: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Closing time in HH:MM")


class DailyOperatingHoursDTO(BaseModel):
    """Operating hours for a single day of the week."""

    model_config = ConfigDict(frozen=True)

    weekday: int = Field(..., ge=1, le=7, description="ISO weekday (1=Monday, 7=Sunday)")
    weekday_name: str
    is_closed: bool = False
    time_ranges: list[TimeRangeDTO] = Field(default_factory=list)


class RestaurantProfileResponse(BaseModel):
    """Full restaurant business profile response DTO."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    restaurant_id: UUID
    organization_id: UUID
    public_name: str
    legal_name: str | None = None
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    address: AddressDTO | None = None
    primary_currency: str
    timezone: str
    schedule: list[DailyOperatingHoursDTO] | None = None
    website_url: str | None = None
    logo_asset_id: UUID | None = None
    banner_asset_id: UUID | None = None
    version: int
    created_at: datetime
    updated_at: datetime


class RestaurantProfileUpdateRequest(BaseModel):
    """Request payload for updating restaurant business profile."""

    model_config = ConfigDict(frozen=True)

    public_name: str | None = None
    legal_name: str | None = None
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    address: AddressDTO | None = None
    primary_currency: str | None = None
    timezone: str | None = None
    schedule: list[DailyOperatingHoursDTO] | None = None
    website_url: str | None = None
    logo_asset_id: UUID | None = None
    banner_asset_id: UUID | None = None
