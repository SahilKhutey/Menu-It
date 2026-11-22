import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# User Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=150)
    organization_name: str = Field(min_length=2, max_length=200)
    restaurant_name: str = Field(min_length=2, max_length=200)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    email: str
    full_name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    is_platform_admin: bool
    status: str
    created_at: datetime


# Organization Schemas
class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    status: str
    created_at: datetime


# Restaurant Schemas
class RestaurantCreate(BaseModel):
    organization_id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    logo_url: str | None = None
    cover_url: str | None = None


class RestaurantUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    logo_url: str | None = None
    cover_url: str | None = None
    status: str | None = None


class RestaurantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    logo_url: str | None = None
    cover_url: str | None = None
    status: str
    created_at: datetime
