"""
ModularMenu — Publishing & Versioning API Schemas (ARC-07 §4.8).
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PublishRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    change_summary: str | None = Field(None, max_length=500)


class PublicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    menu_id: UUID
    menu_version_id: UUID
    version_number: int
    published_by_user_id: UUID
    published_at: datetime
    status: str
    public_url: str


class MenuVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    menu_id: UUID
    version_number: int
    sha256_digest: str
    change_summary: str | None = None
    created_at: datetime


class RollbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_version_id: UUID
    reason: str | None = Field(None, max_length=500)
