"""Common API contracts and value transfer objects (FCD-06 §12.1)."""

from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ResponseMetadata(BaseModel):
    """Metadata envelope present in every API response."""

    model_config = ConfigDict(frozen=True)

    request_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MoneyDTO(BaseModel):
    """Monetary value representation in API contracts."""

    model_config = ConfigDict(frozen=True)

    amount: str
    currency: str


class AddressDTO(BaseModel):
    """Physical address representation in API contracts."""

    model_config = ConfigDict(frozen=True)

    line_1: str
    locality: str
    country_code: str
    line_2: str | None = None
    administrative_area: str | None = None
    postal_code: str | None = None


class APIResponse(BaseModel, Generic[T]):
    """Standardized top-level response envelope."""

    model_config = ConfigDict(frozen=True)

    success: bool
    data: T | None = None
    error: object | None = None
    meta: ResponseMetadata
