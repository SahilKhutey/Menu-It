"""Pagination query parameters and metadata contracts (FCD-07 §13.1)."""

import math
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1, description="1-based page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        """Calculate 0-based database record offset."""
        return (self.page - 1) * self.page_size


class PaginationMeta(BaseModel):
    """Pagination metadata included in paginated responses."""

    model_config = ConfigDict(extra="forbid")

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def build(
        cls,
        *,
        page: int,
        page_size: int,
        total_items: int,
    ) -> "PaginationMeta":
        """Construct pagination metadata from totals and requested page parameters."""
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1 and total_pages > 0,
        )


class PaginatedData(BaseModel, Generic[T]):
    """Standardized payload for paginated collection responses."""

    model_config = ConfigDict(extra="forbid")

    items: list[T]
    pagination: PaginationMeta
