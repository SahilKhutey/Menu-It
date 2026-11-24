"""Domain error to HTTP status code and error code mapping (FCD-07 §10.2)."""

from typing import NamedTuple

from menu_it.api.schemas.errors import ErrorCode
from menu_it.domain.base.errors import (
    BusinessRuleViolationError,
    ConcurrencyConflictError,
    DomainError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    ValidationDomainError,
)


class ErrorMapping(NamedTuple):
    """Mapped HTTP status and public error code."""

    status_code: int
    error_code: ErrorCode


DOMAIN_ERROR_MAPPINGS: dict[type[DomainError], ErrorMapping] = {
    EntityNotFoundError: ErrorMapping(
        status_code=404,
        error_code=ErrorCode.RESOURCE_NOT_FOUND,
    ),
    InvalidStateTransitionError: ErrorMapping(
        status_code=409,
        error_code=ErrorCode.INVALID_STATE_TRANSITION,
    ),
    BusinessRuleViolationError: ErrorMapping(
        status_code=409,
        error_code=ErrorCode.RESOURCE_CONFLICT,
    ),
    ConcurrencyConflictError: ErrorMapping(
        status_code=409,
        error_code=ErrorCode.RESOURCE_CONFLICT,
    ),
    ValidationDomainError: ErrorMapping(
        status_code=422,
        error_code=ErrorCode.VALIDATION_ERROR,
    ),
}


def map_domain_error(exc: DomainError) -> ErrorMapping:
    """Resolve HTTP status and error code for a domain exception."""
    for error_type, mapping in DOMAIN_ERROR_MAPPINGS.items():
        if isinstance(exc, error_type):
            return mapping
    return ErrorMapping(
        status_code=400,
        error_code=ErrorCode.VALIDATION_ERROR,
    )
