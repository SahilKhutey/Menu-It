"""Pydantic schemas for Organization, Membership, and Invitation APIs (FCD-14)."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreateRequest(BaseModel):
    """Payload for onboarding a new tenant organization."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(..., min_length=2, max_length=200)
    slug: str = Field(..., min_length=2, max_length=100)
    currency_code: str = Field(default="INR", min_length=3, max_length=3)
    timezone: str = Field(default="UTC", min_length=1, max_length=100)
    country_code: str = Field(default="IN", min_length=2, max_length=2)
    legal_name: str | None = Field(default=None, max_length=250)
    organization_type: str = Field(default="company", max_length=50)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=30)
    website: str | None = Field(default=None, max_length=500)


class OrganizationUpdateRequest(BaseModel):
    """Payload for updating an organization's profile."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=200)
    legal_name: str | None = Field(default=None, max_length=250)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=30)
    website: str | None = Field(default=None, max_length=500)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    currency_code: str | None = Field(default=None, min_length=3, max_length=3)
    timezone: str | None = Field(default=None, max_length=100)


class OrganizationResponse(BaseModel):
    """Canonical organization DTO."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    name: str
    slug: str
    legal_name: str | None = None
    organization_type: str
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    country_code: str
    currency_code: str
    timezone: str
    status: str
    created_at: datetime
    updated_at: datetime


class OrganizationSettingsUpdateRequest(BaseModel):
    """Payload for updating organization settings."""

    model_config = ConfigDict(extra="forbid")

    settings_payload: dict[str, Any]


class OrganizationSettingsResponse(BaseModel):
    """Organization settings DTO."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    organization_id: UUID
    settings_payload: dict[str, Any]
    updated_at: datetime


class OrganizationMemberResponse(BaseModel):
    """Organization membership DTO."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    status: str
    joined_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class OrganizationMemberUpdateRequest(BaseModel):
    """Payload for updating a member's role or status."""

    model_config = ConfigDict(extra="forbid")

    role: str | None = None
    status: str | None = None


class OwnershipTransferRequest(BaseModel):
    """Payload for transferring organization ownership."""

    model_config = ConfigDict(extra="forbid")

    new_owner_user_id: UUID


class InvitationCreateRequest(BaseModel):
    """Payload for creating an organization membership invitation."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: str = Field(..., min_length=3, max_length=320)
    role: str = Field(default="staff")


class InvitationAcceptRequest(BaseModel):
    """Payload for accepting an organization invitation token."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    token: str = Field(..., min_length=10, max_length=256)


class InvitationResponse(BaseModel):
    """Organization invitation DTO (never exposes token hash)."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    organization_id: UUID
    email: str
    role: str
    status: str
    expires_at: datetime
    invited_by: UUID | None = None
    accepted_by: UUID | None = None
    accepted_at: datetime | None = None
    created_at: datetime
