"""
ModularMenu — Organization & Tenancy API Schemas (ARC-07 §4.2).
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=180)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    country_code: str = Field(default="IN", min_length=2, max_length=2)
    default_currency: str = Field(default="INR", min_length=3, max_length=3)


class OrganizationUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(None, min_length=1, max_length=180)
    default_currency: str | None = Field(None, min_length=3, max_length=3)


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    status: str
    country_code: str = "IN"
    default_currency: str = "INR"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OrganizationMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    status: str
    created_at: datetime


class InvitationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    role: str = Field(
        default="restaurant_manager", pattern=r"^(admin|restaurant_manager|menu_editor|viewer)$"
    )


class InvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    email: str
    role: str
    status: str
    expires_at: datetime
    created_at: datetime
