"""
ModularMenu — API Cursor & Offset Pagination Dependencies (ARC-07 §8.1).
Enforces bounded limits (default 20, max 100) and opaque cursor parsing.
"""
from typing import Generic, List, Optional, TypeVar
from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams:
    def __init__(
        self,
        cursor: Optional[str] = Query(None, description="Opaque pagination cursor token"),
        limit: int = Query(20, ge=1, le=100, description="Page size limit (1-100)"),
    ):
        self.cursor = cursor
        self.limit = limit


class CursorPaginationMeta(BaseModel):
    limit: int
    next_cursor: Optional[str] = None
    has_more: bool = False


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: dict
