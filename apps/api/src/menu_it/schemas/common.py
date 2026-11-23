"""Common API response contracts."""

from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMetadata(BaseModel):
    request_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class APIError(BaseModel):
    code: str
    message: str
    details: list[dict[str, object]] = Field(default_factory=list)


class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: APIError | None = None
    meta: ResponseMetadata
