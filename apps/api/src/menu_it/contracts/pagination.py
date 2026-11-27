"""Pagination query and metadata contracts (FCD-06 §12.3)."""

import math
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from menu_it.contracts.common import ResponseMetadata

T = TypeVar("T")


class PaginationQuery(BaseModel):
    """Query parameters for paginated endpoints."""

    model_config = ConfigDict(frozen=True)

    page: int = Field(default=1, ge=1, description="1-based page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginationMeta(BaseModel):
    """Pagination metadata included in paginated responses."""

    model_config = ConfigDict(frozen=True)

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


def build_pagination_meta(total_items: int, page: int, page_size: int) -> PaginationMeta:
    """Construct pagination metadata from totals and requested page parameters."""
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    return PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1 and total_pages > 0,
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized response envelope for paginated resource collections."""

    model_config = ConfigDict(frozen=True)

    data: list[T]
    pagination: PaginationMeta
    meta: ResponseMetadata
