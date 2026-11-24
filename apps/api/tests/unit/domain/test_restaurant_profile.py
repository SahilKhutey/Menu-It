"""Unit tests for RestaurantProfile aggregate root (FCD-06)."""

from datetime import time
from uuid import uuid4

import pytest

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.restaurant.events import (
    RestaurantOperatingHoursUpdated,
    RestaurantProfileUpdated,
)
from menu_it.domain.restaurant.profile import RestaurantProfile
from menu_it.domain.value_objects.address import Address
from menu_it.domain.value_objects.contact import EmailAddress
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.operating_hours import WeeklyOperatingSchedule
from menu_it.domain.value_objects.phone_number import PhoneNumber
from menu_it.domain.value_objects.timezone import TimeZone


def test_create_restaurant_profile_success() -> None:
    rest_id = uuid4()
    org_id = uuid4()
    profile = RestaurantProfile.create(
        restaurant_id=rest_id,
        organization_id=org_id,
        public_name="The Gourmet Bistro",
        primary_currency=Currency("USD"),
        timezone=TimeZone("America/New_York"),
    )

    assert profile.restaurant_id == rest_id
    assert profile.organization_id == org_id
    assert profile.public_name == "The Gourmet Bistro"
    assert profile.primary_currency.code == "USD"
    assert profile.timezone.name == "America/New_York"
    assert profile.version == 1

    events = profile.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], RestaurantProfileUpdated)
    assert events[0].profile_id == profile.id
    assert events[0].changed_fields == ("__created__",)
    assert events[0].version == 1
    assert len(profile.collect_events()) == 0


def test_create_restaurant_profile_empty_name_raises() -> None:
    with pytest.raises(ValidationDomainError, match="cannot be empty"):
        RestaurantProfile.create(
            restaurant_id=uuid4(),
            organization_id=uuid4(),
            public_name="   ",
            primary_currency=Currency("USD"),
            timezone=TimeZone("UTC"),
        )


def test_profile_mutations_and_event_recording() -> None:
    profile = RestaurantProfile.create(
        restaurant_id=uuid4(),
        organization_id=uuid4(),
        public_name="Bistro Initial",
        primary_currency=Currency("USD"),
        timezone=TimeZone("UTC"),
    )
    profile.collect_events()  # Clear creation event

    # 1. Update public name
    profile.update_public_name("Bistro Deluxe")
    assert profile.public_name == "Bistro Deluxe"
    assert profile.version == 2

    # 2. Update legal name and description
    profile.update_legal_name("Bistro Holdings LLC")
    profile.update_description("Fine dining experience.")
    assert profile.legal_name == "Bistro Holdings LLC"
    assert profile.description == "Fine dining experience."
    assert profile.version == 4

    # 3. Update contact info
    email = EmailAddress("contact@bistro.com")
    phone = PhoneNumber("+14155552671")
    profile.update_contact(email=email, phone=phone)
    assert profile.email == email
    assert profile.phone == phone
    assert profile.version == 5

    # 4. Update address
    addr = Address(
        line_1="123 Main St",
        locality="San Francisco",
        country_code="US",
        postal_code="94105",
    )
    profile.update_address(addr)
    assert profile.address == addr
    assert profile.version == 6

    # 5. Update localization
    profile.update_localization(
        currency=Currency("EUR"),
        timezone=TimeZone("Europe/Paris"),
    )
    assert profile.primary_currency.code == "EUR"
    assert profile.timezone.name == "Europe/Paris"
    assert profile.version == 7

    # 6. Update website and media
    profile.update_website_url("https://bistro.com")
    logo_id = uuid4()
    banner_id = uuid4()
    profile.update_media(logo_asset_id=logo_id, banner_asset_id=banner_id)
    assert profile.website_url == "https://bistro.com"
    assert profile.logo_asset_id == logo_id
    assert profile.banner_asset_id == banner_id
    assert profile.version == 9

    events = profile.collect_events()
    assert len(events) == 8  # 8 mutations


def test_profile_schedule_mutation() -> None:
    profile = RestaurantProfile.create(
        restaurant_id=uuid4(),
        organization_id=uuid4(),
        public_name="Cafe Central",
        primary_currency=Currency("GBP"),
        timezone=TimeZone("Europe/London"),
    )
    profile.collect_events()

    schedule = WeeklyOperatingSchedule.create_standard(
        opens_at=time(8, 0),
        closes_at=time(20, 0),
    )
    profile.update_schedule(schedule)

    assert profile.schedule == schedule
    assert profile.version == 2

    events = profile.collect_events()
    assert len(events) == 2
    types = [type(e) for e in events]
    assert RestaurantOperatingHoursUpdated in types
    assert RestaurantProfileUpdated in types
