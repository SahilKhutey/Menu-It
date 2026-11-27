"""Pydantic request and response schemas for Branch & Assignment APIs (FCD-14)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BranchCreateRequest(BaseModel):
    """Payload for creating a physical restaurant branch."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(..., min_length=2, max_length=200)
    slug: str = Field(..., min_length=2, max_length=100)
    timezone: str = Field(default="UTC", max_length=100)
    country_code: str = Field(default="IN", min_length=2, max_length=2)
    branch_code: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=30)
    address_line_1: str | None = Field(default=None, max_length=250)
    address_line_2: str | None = Field(default=None, max_length=250)
    city: str | None = Field(default=None, max_length=120)
    state_region: str | None = Field(default=None, max_length=120)
    postal_code: str | None = Field(default=None, max_length=30)
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class BranchUpdateRequest(BaseModel):
    """Payload for updating branch operational and address details."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=200)
    branch_code: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=30)
    address_line_1: str | None = Field(default=None, max_length=250)
    address_line_2: str | None = Field(default=None, max_length=250)
    city: str | None = Field(default=None, max_length=120)
    state_region: str | None = Field(default=None, max_length=120)
    postal_code: str | None = Field(default=None, max_length=30)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    timezone: str | None = Field(default=None, max_length=100)


class BranchResponse(BaseModel):
    """Canonical branch DTO."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    name: str
    slug: str
    branch_code: str | None = None
    email: str | None = None
    phone: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state_region: str | None = None
    postal_code: str | None = None
    country_code: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    timezone: str
    status: str
    created_at: datetime
    updated_at: datetime


class BranchAssignmentUpsertRequest(BaseModel):
    """Payload for assigning or updating a user's branch role."""

    model_config = ConfigDict(extra="forbid")

    role: str = Field(default="branch_staff")


class BranchAssignmentResponse(BaseModel):
    """Canonical branch assignment DTO."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    branch_id: UUID
    user_id: UUID
    role: str
    status: str
    created_at: datetime
    updated_at: datetime
