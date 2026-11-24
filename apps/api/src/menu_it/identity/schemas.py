"""Identity Pydantic response and update schemas (FCD-05 §7.2)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from menu_it.database.models.user import UserStatus


class UserResponse(BaseModel):
    """Safe user profile response omitting credentials and security tokens."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    display_name: str
    email_verified: bool
    status: UserStatus
    created_at: datetime
    updated_at: datetime


class UserProfileUpdateRequest(BaseModel):
    """Permitted fields for user profile updates."""

    display_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=160,
    )
