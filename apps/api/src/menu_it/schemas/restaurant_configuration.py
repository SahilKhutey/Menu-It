"""Pydantic schemas for FCD-15 Restaurant Profile, Branding & Operational Configuration."""

from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RestaurantProfileConfigResponse(BaseModel):
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    display_name: str
    short_description: str | None = None
    description: str | None = None
    cuisine_type: str | None = None
    price_range: str | None = None
    website_url: str | None = None
    public_email: str | None = None
    public_phone: str | None = None
    social_links: dict[str, Any] = Field(default_factory=dict)
    version: int


class RestaurantProfileConfigUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, min_length=2, max_length=200)
    short_description: str | None = Field(default=None, max_length=300)
    description: str | None = None
    cuisine_type: str | None = Field(default=None, max_length=100)
    price_range: str | None = Field(default=None, max_length=20)
    website_url: str | None = Field(default=None, max_length=500)
    public_email: str | None = Field(default=None, max_length=320)
    public_phone: str | None = Field(default=None, max_length=30)
    social_links: dict[str, Any] | None = None
    expected_version: int | None = None


class RestaurantBrandingResponse(BaseModel):
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    logo_asset_id: UUID | None = None
    alternate_logo_asset_id: UUID | None = None
    cover_asset_id: UUID | None = None
    favicon_asset_id: UUID | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    accent_color: str | None = None
    background_color: str | None = None
    text_color: str | None = None
    font_family: str | None = None
    border_radius: str | None = None
    theme_preset: str | None = None
    theme_settings: dict[str, Any] = Field(default_factory=dict)
    revision: int


class RestaurantBrandingUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    logo_asset_id: UUID | None = None
    alternate_logo_asset_id: UUID | None = None
    cover_asset_id: UUID | None = None
    favicon_asset_id: UUID | None = None
    primary_color: str | None = Field(default=None, max_length=7)
    secondary_color: str | None = Field(default=None, max_length=7)
    accent_color: str | None = Field(default=None, max_length=7)
    background_color: str | None = Field(default=None, max_length=7)
    text_color: str | None = Field(default=None, max_length=7)
    font_family: str | None = Field(default=None, max_length=100)
    border_radius: str | None = Field(default=None, max_length=20)
    theme_preset: str | None = Field(default=None, max_length=60)
    theme_settings: dict[str, Any] | None = None
    expected_revision: int | None = None


class OpeningIntervalSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opens_at: time
    closes_at: time
    closes_next_day: bool = False


class DailyScheduleInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day_of_week: int = Field(ge=0, le=6)
    is_closed: bool = False
    intervals: list[OpeningIntervalSchema] = Field(default_factory=list)


class WeeklyHoursReplaceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    days: list[DailyScheduleInput]


class WeeklyHourRowResponse(BaseModel):
    id: UUID
    day_of_week: int
    opens_at: time | None = None
    closes_at: time | None = None
    closes_next_day: bool
    is_closed: bool


class ScheduleExceptionUpsertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    exception_date: date
    exception_type: str
    reason: str | None = Field(default=None, max_length=250)
    intervals: list[OpeningIntervalSchema] = Field(default_factory=list)


class ScheduleExceptionResponse(BaseModel):
    id: UUID
    exception_date: date
    exception_type: str
    reason: str | None = None
    intervals_payload: list[dict[str, Any]] = Field(default_factory=list)


class ServiceModeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_type: str
    enabled: bool
    requires_customer_address: bool = False
    accepts_scheduled_orders: bool = False
    minimum_notice_minutes: int = Field(default=0, ge=0)


class ServiceModesUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modes: list[ServiceModeInput]


class ServiceModeResponse(BaseModel):
    id: UUID
    service_type: str
    enabled: bool
    configuration: dict[str, Any] = Field(default_factory=dict)


class OperationalSettingsResponse(BaseModel):
    id: UUID
    preparation_buffer_minutes: int
    minimum_notice_minutes: int
    maximum_advance_days: int
    max_concurrent_orders: int | None = None
    auto_accept_orders: bool
    holiday_behavior: str
    revision: int


class OperationalSettingsUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preparation_buffer_minutes: int = Field(ge=0)
    minimum_notice_minutes: int = Field(ge=0)
    maximum_advance_days: int = Field(ge=0)
    max_concurrent_orders: int | None = Field(default=None, ge=1)
    auto_accept_orders: bool = False
    holiday_behavior: str = Field(default="follow_exceptions", max_length=40)


class BranchConfigurationUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name_override: str | None = Field(default=None, max_length=200)
    public_phone_override: str | None = Field(default=None, max_length=30)
    schedule_override_enabled: bool | None = None
    service_override_enabled: bool | None = None
    settings: dict[str, Any] | None = None


class BranchConfigurationResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reset_schedule: bool = True
    reset_services: bool = True


class EffectiveConfigurationResponse(BaseModel):
    organization_id: UUID
    restaurant_id: UUID
    branch_id: UUID | None = None
    display_name: str
    timezone: str
    currency_code: str
    public_phone: str | None = None
    enabled_services: list[str]
    operational_settings: dict[str, Any]
    revision: int


class PublishProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    public_slug: str | None = Field(default=None, max_length=120)
    change_summary: str | None = Field(default=None, max_length=250)


class RestaurantPublicationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    public_slug: str
    status: str
    published_revision: int | None = None
    published_at: datetime | None = None


class ConfigurationRevisionResponse(BaseModel):
    id: UUID
    revision_number: int
    change_summary: str | None = None
    created_at: datetime
