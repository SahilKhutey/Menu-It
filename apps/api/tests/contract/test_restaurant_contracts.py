"""Contract tests verifying restaurant profile API schemas (FCD-06)."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from menu_it.contracts.common import AddressDTO
from menu_it.contracts.restaurant import (
    DailyOperatingHoursDTO,
    RestaurantProfileResponse,
    RestaurantProfileUpdateRequest,
    TimeRangeDTO,
)


def test_time_range_dto_pattern() -> None:
    valid = TimeRangeDTO(opens_at="09:00", closes_at="17:00")
    assert valid.opens_at == "09:00"

    with pytest.raises(ValidationError):
        TimeRangeDTO(opens_at="9:00", closes_at="17:00")  # requires 2 digits for hour


def test_restaurant_profile_response_contract() -> None:
    now = datetime.now(UTC)
    resp = RestaurantProfileResponse(
        id=uuid4(),
        restaurant_id=uuid4(),
        organization_id=uuid4(),
        public_name="Le Petit Bistro",
        legal_name="LPB Dining Inc",
        description="Authentic bistro",
        email="contact@lpb.com",
        phone="+14155552671",
        address=AddressDTO(
            line_1="10 Rue De Paris",
            locality="Paris",
            country_code="FR",
        ),
        primary_currency="EUR",
        timezone="Europe/Paris",
        schedule=[
            DailyOperatingHoursDTO(
                weekday=1,
                weekday_name="MONDAY",
                is_closed=False,
                time_ranges=[TimeRangeDTO(opens_at="09:00", closes_at="18:00")],
            )
        ],
        version=1,
        created_at=now,
        updated_at=now,
    )

    dumped = resp.model_dump(mode="json")
    assert dumped["public_name"] == "Le Petit Bistro"
    assert dumped["primary_currency"] == "EUR"
    assert len(dumped["schedule"]) == 1
    assert dumped["schedule"][0]["weekday"] == 1


def test_restaurant_profile_update_request_contract() -> None:
    req = RestaurantProfileUpdateRequest(
        public_name="New Bistro Name",
        primary_currency="USD",
    )
    dumped = req.model_dump(exclude_unset=True)
    assert dumped == {"public_name": "New Bistro Name", "primary_currency": "USD"}
