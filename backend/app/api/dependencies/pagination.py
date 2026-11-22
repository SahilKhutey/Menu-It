"""
ModularMenu — API Cursor & Offset Pagination Dependencies (ARC-07 §8.1).
Enforces bounded limits (default 20, max 100) and opaque cursor parsing.
"""

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    def __init__(
        self,
        cursor: str | None = Query(None, description="Opaque pagination cursor token"),
        limit: int = Query(20, ge=1, le=100, description="Page size limit (1-100)"),
    ):
        self.cursor = cursor
        self.limit = limit


class CursorPaginationMeta(BaseModel):
    limit: int
    next_cursor: str | None = None
    has_more: bool = False


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: dict
