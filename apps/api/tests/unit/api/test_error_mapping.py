"""Unit tests for domain error to HTTP status mapping (FCD-07 WP-04)."""

from menu_it.api.exceptions.mapping import map_domain_error
from menu_it.api.schemas.errors import ErrorCode
from menu_it.domain.base.errors import (
    BusinessRuleViolationError,
    ConcurrencyConflictError,
    DomainError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    ValidationDomainError,
)


def test_entity_not_found_mapping():
    err = EntityNotFoundError("Restaurant", "123")
    mapping = map_domain_error(err)
    assert mapping.status_code == 404
    assert mapping.error_code == ErrorCode.RESOURCE_NOT_FOUND


def test_invalid_state_transition_mapping():
    err = InvalidStateTransitionError("Restaurant", "active", "archived")
    mapping = map_domain_error(err)
    assert mapping.status_code == 409
    assert mapping.error_code == ErrorCode.INVALID_STATE_TRANSITION


def test_concurrency_conflict_mapping():
    err = ConcurrencyConflictError("RestaurantProfile version conflict")
    mapping = map_domain_error(err)
    assert mapping.status_code == 409
    assert mapping.error_code == ErrorCode.RESOURCE_CONFLICT


def test_business_rule_violation_mapping():
    err = BusinessRuleViolationError("Restaurant", "Cannot close already closed venue")
    mapping = map_domain_error(err)
    assert mapping.status_code == 409
    assert mapping.error_code == ErrorCode.RESOURCE_CONFLICT


def test_validation_domain_error_mapping():
    err = ValidationDomainError("Invalid currency")
    mapping = map_domain_error(err)
    assert mapping.status_code == 422
    assert mapping.error_code == ErrorCode.VALIDATION_ERROR


def test_unknown_domain_error_mapping():
    err = DomainError("Generic domain error")
    mapping = map_domain_error(err)
    assert mapping.status_code == 400
    assert mapping.error_code == ErrorCode.VALIDATION_ERROR
