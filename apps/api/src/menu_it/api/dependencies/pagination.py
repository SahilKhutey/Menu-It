"""Pagination query parameter dependency (FCD-07 §13.1)."""

from fastapi import Query

from menu_it.api.schemas.pagination import PaginationParams


def get_pagination_params(
    page: int = Query(default=1, ge=1, description="1-based page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginationParams:
    """Extract and validate pagination query parameters."""
    return PaginationParams(page=page, page_size=page_size)
