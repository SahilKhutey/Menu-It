"""Integration tests for SQLAlchemyRestaurantProfileRepository (FCD-06 §14)."""

from datetime import time
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.domain.base.errors import ConcurrencyConflictError
from menu_it.domain.restaurant.profile import RestaurantProfile
from menu_it.domain.value_objects.address import Address
from menu_it.domain.value_objects.contact import EmailAddress
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.operating_hours import WeeklyOperatingSchedule
from menu_it.domain.value_objects.phone_number import PhoneNumber
from menu_it.domain.value_objects.timezone import TimeZone
from menu_it.infrastructure.repositories.restaurant_profile_repository import (
    SQLAlchemyRestaurantProfileRepository,
)


@pytest.mark.asyncio
async def test_repository_save_and_retrieve_by_id(db_session: AsyncSession) -> None:
    # 1. Setup organization and restaurant
    org = Organization(
        name="Test Org", slug=f"test-org-{uuid4().hex[:6]}", status=OrganizationStatus.ACTIVE
    )
    db_session.add(org)
    await db_session.commit()

    rest = Restaurant(
        organization_id=org.id,
        name="Main Restaurant",
        slug=f"main-rest-{uuid4().hex[:6]}",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add(rest)
    await db_session.commit()

    repo = SQLAlchemyRestaurantProfileRepository(db_session)

    # 2. Create domain aggregate
    profile = RestaurantProfile.create(
        restaurant_id=rest.id,
        organization_id=org.id,
        public_name="The Gourmet Spot",
        primary_currency=Currency("USD"),
        timezone=TimeZone("America/New_York"),
        legal_name="Gourmet Spot LLC",
        description="Fine dining venue",
        email=EmailAddress("hello@gourmetspot.com"),
        phone=PhoneNumber("+14155552671"),
        address=Address(
            line_1="789 Market St",
            locality="San Francisco",
            country_code="US",
            postal_code="94103",
        ),
        schedule=WeeklyOperatingSchedule.create_standard(
            opens_at=time(10, 0),
            closes_at=time(22, 0),
        ),
    )

    # 3. Save to database
    await repo.save(profile)
    await db_session.commit()

    # 4. Retrieve by ID
    loaded_by_id = await repo.get_by_id(profile.id)
    assert loaded_by_id is not None
    assert loaded_by_id.id == profile.id
    assert loaded_by_id.restaurant_id == rest.id
    assert loaded_by_id.organization_id == org.id
    assert loaded_by_id.public_name == "The Gourmet Spot"
    assert loaded_by_id.legal_name == "Gourmet Spot LLC"
    assert loaded_by_id.primary_currency.code == "USD"
    assert loaded_by_id.timezone.name == "America/New_York"
    assert loaded_by_id.email is not None and loaded_by_id.email.value == "hello@gourmetspot.com"
    assert loaded_by_id.phone is not None and loaded_by_id.phone.e164 == "+14155552671"
    assert loaded_by_id.address is not None and loaded_by_id.address.locality == "San Francisco"
    assert loaded_by_id.schedule is not None and len(loaded_by_id.schedule.days) == 7

    # 5. Retrieve by restaurant_id and organization_id
    loaded_by_rest = await repo.get_by_restaurant_id(rest.id, org.id)
    assert loaded_by_rest is not None
    assert loaded_by_rest.id == profile.id

    # 6. Mismatched organization_id returns None
    loaded_wrong_org = await repo.get_by_restaurant_id(rest.id, uuid4())
    assert loaded_wrong_org is None


@pytest.mark.asyncio
async def test_repository_update_mutations(db_session: AsyncSession) -> None:
    org = Organization(
        name="Update Org", slug=f"update-org-{uuid4().hex[:6]}", status=OrganizationStatus.ACTIVE
    )
    db_session.add(org)
    await db_session.commit()

    rest = Restaurant(
        organization_id=org.id,
        name="Update Rest",
        slug=f"update-rest-{uuid4().hex[:6]}",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add(rest)
    await db_session.commit()

    repo = SQLAlchemyRestaurantProfileRepository(db_session)
    profile = RestaurantProfile.create(
        restaurant_id=rest.id,
        organization_id=org.id,
        public_name="Initial Name",
        primary_currency=Currency("USD"),
        timezone=TimeZone("UTC"),
    )
    await repo.save(profile)
    await db_session.commit()

    # Mutate aggregate
    profile.update_public_name("Updated Name")
    profile.update_localization(Currency("EUR"), TimeZone("Europe/London"))
    await repo.save(profile)
    await db_session.commit()

    reloaded = await repo.get_by_id(profile.id)
    assert reloaded is not None
    assert reloaded.public_name == "Updated Name"
    assert reloaded.primary_currency.code == "EUR"
    assert reloaded.timezone.name == "Europe/London"
    assert reloaded.version == 3


@pytest.mark.asyncio
async def test_repository_optimistic_concurrency_conflict(db_session: AsyncSession) -> None:
    org = Organization(
        name="Conflict Org",
        slug=f"conflict-org-{uuid4().hex[:6]}",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org)
    await db_session.commit()

    rest = Restaurant(
        organization_id=org.id,
        name="Conflict Rest",
        slug=f"conflict-rest-{uuid4().hex[:6]}",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add(rest)
    await db_session.commit()

    repo = SQLAlchemyRestaurantProfileRepository(db_session)
    profile = RestaurantProfile.create(
        restaurant_id=rest.id,
        organization_id=org.id,
        public_name="Base Name",
        primary_currency=Currency("USD"),
        timezone=TimeZone("UTC"),
    )
    await repo.save(profile)
    await db_session.commit()

    # Create stale copy with version 1
    stale_profile = await repo.get_by_id(profile.id)
    assert stale_profile is not None

    # Advance DB version by saving another update
    profile.update_public_name("Winner Update")
    await repo.save(profile)
    await db_session.commit()

    # Try saving stale profile without advancing its version past DB version
    stale_profile.public_name = "Stale Update"
    stale_profile.version = 1  # Behind DB version 2
    with pytest.raises(ConcurrencyConflictError, match="Concurrency conflict"):
        await repo.save(stale_profile)
