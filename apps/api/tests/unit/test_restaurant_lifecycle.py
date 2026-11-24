"""Unit tests for restaurant lifecycle transitions (FCD-04 §15)."""

from uuid import uuid4

import pytest

from menu_it.database.models.restaurant import (
    Restaurant,
    RestaurantStatus,
)
from menu_it.services.restaurant_lifecycle import (
    InvalidRestaurantTransition,
    transition_restaurant,
)


def test_active_transitions():
    """Verify ACTIVE restaurant can transition to INACTIVE, SUSPENDED, and ARCHIVED."""
    rest = Restaurant(
        organization_id=uuid4(),
        name="Branch Downtown",
        slug="downtown",
        status=RestaurantStatus.ACTIVE,
    )

    # ACTIVE -> INACTIVE -> ACTIVE
    transition_restaurant(rest, RestaurantStatus.INACTIVE)
    assert rest.status == RestaurantStatus.INACTIVE
    transition_restaurant(rest, RestaurantStatus.ACTIVE)
    assert rest.status == RestaurantStatus.ACTIVE

    # ACTIVE -> SUSPENDED -> ACTIVE
    transition_restaurant(rest, RestaurantStatus.SUSPENDED)
    assert rest.status == RestaurantStatus.SUSPENDED
    transition_restaurant(rest, RestaurantStatus.ACTIVE)
    assert rest.status == RestaurantStatus.ACTIVE


def test_archived_is_terminal():
    """Verify ARCHIVED restaurant cannot transition to any other status."""
    rest = Restaurant(
        organization_id=uuid4(),
        name="Old Branch",
        slug="old-branch",
        status=RestaurantStatus.ARCHIVED,
    )
    with pytest.raises(InvalidRestaurantTransition):
        transition_restaurant(rest, RestaurantStatus.ACTIVE)


def test_illegal_restaurant_transition():
    """Verify identical status returns current state without error."""
    rest = Restaurant(
        organization_id=uuid4(),
        name="Test Branch",
        slug="test-branch",
        status=RestaurantStatus.ACTIVE,
    )
    assert transition_restaurant(rest, RestaurantStatus.ACTIVE) == RestaurantStatus.ACTIVE
