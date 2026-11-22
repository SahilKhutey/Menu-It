"""
ModularMenu — API Common Envelope Schemas (ARC-07 §5.4).
Enforces consistent data/meta envelopes without leaking raw ORM models.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    limit: int = 20
    next_cursor: str | None = None
    has_more: bool = False


class ResponseMeta(BaseModel):
    request_id: str | None = None
    pagination: PaginationMeta | None = None


class SuccessEnvelope(BaseModel, Generic[T]):
    """Standard success envelope: {"data": T, "meta": {"request_id": str}}"""

    model_config = ConfigDict(from_attributes=True)
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class PaginatedEnvelope(BaseModel, Generic[T]):
    """Standard paginated envelope: {"data": [T], "meta": {"request_id": str, "pagination": ...}}"""

    model_config = ConfigDict(from_attributes=True)
    data: list[T]
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
