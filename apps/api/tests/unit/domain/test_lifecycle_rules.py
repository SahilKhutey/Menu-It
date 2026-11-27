"""Unit tests for restaurant lifecycle state transitions and tenant ownership (FCD-06)."""

from uuid import uuid4

import pytest

from menu_it.domain.base.errors import (
    BusinessRuleViolationError,
    InvalidStateTransitionError,
    ValidationDomainError,
)
from menu_it.domain.restaurant.lifecycle import (
    RestaurantLifecycleState,
    validate_restaurant_transition,
)
from menu_it.domain.restaurant.ownership import assert_restaurant_belongs_to_organization


def test_allowed_state_transitions() -> None:
    # From ACTIVE
    validate_restaurant_transition(
        RestaurantLifecycleState.ACTIVE,
        RestaurantLifecycleState.INACTIVE,
    )
    validate_restaurant_transition(
        RestaurantLifecycleState.ACTIVE,
        RestaurantLifecycleState.SUSPENDED,
    )
    validate_restaurant_transition(
        RestaurantLifecycleState.ACTIVE,
        RestaurantLifecycleState.ARCHIVED,
    )

    # From INACTIVE
    validate_restaurant_transition(
        RestaurantLifecycleState.INACTIVE,
        RestaurantLifecycleState.ACTIVE,
    )
    validate_restaurant_transition(
        RestaurantLifecycleState.INACTIVE,
        RestaurantLifecycleState.ARCHIVED,
    )

    # From SUSPENDED
    validate_restaurant_transition(
        RestaurantLifecycleState.SUSPENDED,
        RestaurantLifecycleState.ACTIVE,
    )
    validate_restaurant_transition(
        RestaurantLifecycleState.SUSPENDED,
        RestaurantLifecycleState.ARCHIVED,
    )


def test_prohibited_transitions_raise() -> None:
    # ARCHIVED is terminal
    with pytest.raises(InvalidStateTransitionError, match="Cannot transition restaurant"):
        validate_restaurant_transition(
            RestaurantLifecycleState.ARCHIVED,
            RestaurantLifecycleState.ACTIVE,
        )

    with pytest.raises(InvalidStateTransitionError, match="Cannot transition restaurant"):
        validate_restaurant_transition(
            RestaurantLifecycleState.ARCHIVED,
            RestaurantLifecycleState.INACTIVE,
        )

    # INACTIVE cannot transition directly to SUSPENDED
    with pytest.raises(InvalidStateTransitionError, match="Cannot transition restaurant"):
        validate_restaurant_transition(
            RestaurantLifecycleState.INACTIVE,
            RestaurantLifecycleState.SUSPENDED,
        )


def test_same_state_is_noop() -> None:
    validate_restaurant_transition(
        RestaurantLifecycleState.ACTIVE,
        RestaurantLifecycleState.ACTIVE,
    )


def test_invalid_state_name_raises() -> None:
    with pytest.raises(ValidationDomainError, match="Invalid restaurant lifecycle state"):
        validate_restaurant_transition(RestaurantLifecycleState.ACTIVE, "nonexistent")


def test_tenant_ownership_invariant() -> None:
    matching_org_id = uuid4()
    # Matching org IDs succeed silently
    assert_restaurant_belongs_to_organization(
        restaurant_org_id=matching_org_id,
        context_org_id=matching_org_id,
    )

    other_org_id = uuid4()
    with pytest.raises(BusinessRuleViolationError, match="Tenant ownership mismatch"):
        assert_restaurant_belongs_to_organization(
            restaurant_org_id=matching_org_id,
            context_org_id=other_org_id,
        )
