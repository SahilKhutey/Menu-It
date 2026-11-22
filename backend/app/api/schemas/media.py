"""
ModularMenu — Media API Schemas (ARC-07 §4.9).
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UploadIntentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(pattern=r"^image\/(jpeg|png|webp|svg\+xml)$")
    byte_size: int = Field(gt=0, le=10 * 1024 * 1024)  # Max 10MB


class UploadIntentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    media_id: UUID
    upload_url: str
    storage_path: str
    expires_at: datetime
    headers_required: dict = Field(default_factory=dict)


class UploadCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    media_id: UUID
    etag: str | None = None


class MediaAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    file_name: str
    mime_type: str
    byte_size: int
    storage_path: str
    public_url: str
    created_at: datetime | None = None
    created_at: datetime
