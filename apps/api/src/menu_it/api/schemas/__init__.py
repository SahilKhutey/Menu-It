"""API schemas package (FCD-07)."""

from menu_it.api.schemas.common import (
    APIError,
    APIErrorDetail,
    APIResponse,
    ResponseMeta,
)
from menu_it.api.schemas.errors import ErrorCode
from menu_it.api.schemas.pagination import (
    PaginatedData,
    PaginationMeta,
    PaginationParams,
)

__all__ = [
    "APIError",
    "APIErrorDetail",
    "APIResponse",
    "ErrorCode",
    "PaginatedData",
    "PaginationMeta",
    "PaginationParams",
    "ResponseMeta",
]
