"""Shared API transport contracts module (FCD-06 §12)."""

from menu_it.contracts.common import (
    AddressDTO,
    APIResponse,
    MoneyDTO,
    ResponseMetadata,
)
from menu_it.contracts.errors import APIError, APIErrorDetail
from menu_it.contracts.organization import OrganizationReferenceResponse
from menu_it.contracts.pagination import (
    PaginatedResponse,
    PaginationMeta,
    PaginationQuery,
    build_pagination_meta,
)
from menu_it.contracts.restaurant import (
    DailyOperatingHoursDTO,
    RestaurantProfileResponse,
    RestaurantProfileUpdateRequest,
    TimeRangeDTO,
)

__all__ = [
    "APIError",
    "APIErrorDetail",
    "APIResponse",
    "AddressDTO",
    "DailyOperatingHoursDTO",
    "MoneyDTO",
    "OrganizationReferenceResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "PaginationQuery",
    "RestaurantProfileResponse",
    "RestaurantProfileUpdateRequest",
    "ResponseMetadata",
    "TimeRangeDTO",
    "build_pagination_meta",
]
