"""Common API transport contracts and response envelope (FCD-07 §8.1)."""

from datetime import UTC, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Metadata envelope present in every API response."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class APIErrorDetail(BaseModel):
    """Normalized field-specific error detail."""

    model_config = ConfigDict(extra="forbid")

    field: str | None = None
    code: str
    message: str


class APIError(BaseModel):
    """Structured error payload envelope."""

    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: list[APIErrorDetail] = Field(default_factory=list)


class APIResponse(BaseModel, Generic[T]):
    """Standardized top-level response envelope conforming to FCD-02/FCD-07."""

    model_config = ConfigDict(extra="forbid")

    success: bool
    data: T | None = None
    error: APIError | None = None
    meta: ResponseMeta
