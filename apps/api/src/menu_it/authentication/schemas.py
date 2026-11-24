"""Pydantic schemas for authentication and session endpoints (FCD-05 §7.2)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from menu_it.identity.schemas import UserResponse


class RegisterRequest(BaseModel):
    """Payload for self-service user registration."""

    email: EmailStr
    display_name: str = Field(
        min_length=2,
        max_length=160,
    )
    password: str = Field(
        min_length=12,
        max_length=128,
    )


class LoginRequest(BaseModel):
    """Payload for local email and password authentication."""

    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=128,
    )


class TokenRefreshRequest(BaseModel):
    """Optional JSON body for refresh operations when cookies are not utilized."""

    refresh_token: str | None = Field(
        default=None,
        description="Opaque refresh token string",
    )


class AuthenticationResponse(BaseModel):
    """Standardized response following successful authentication."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse
    refresh_token: str | None = None


class TokenResponse(BaseModel):
    """Response returned upon refresh token rotation."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: str | None = None


class PasswordForgotRequest(BaseModel):
    """Payload to initiate self-service password recovery."""

    email: EmailStr


class PasswordResetRequest(BaseModel):
    """Payload to complete password reset using a recovery token."""

    token: str = Field(min_length=16)
    new_password: str = Field(
        min_length=12,
        max_length=128,
    )


class PasswordChangeRequest(BaseModel):
    """Payload for authenticated password modification."""

    current_password: str = Field(min_length=1)
    new_password: str = Field(
        min_length=12,
        max_length=128,
    )


class EmailVerificationRequest(BaseModel):
    """Payload to complete email address verification."""

    token: str = Field(min_length=16)


class ResendVerificationRequest(BaseModel):
    """Payload to request another verification email."""

    email: EmailStr


class SessionResponse(BaseModel):
    """Safe session metadata representation for device management."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ip_address: str | None = None
    user_agent: str | None = None
    last_activity_at: datetime
    expires_at: datetime
