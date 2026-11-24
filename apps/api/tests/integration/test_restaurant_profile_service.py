"""Integration tests for UpdateRestaurantProfileService (FCD-06 §15)."""

from datetime import time
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.domain.base.domain_event import DomainEvent
from menu_it.domain.base.errors import EntityNotFoundError
from menu_it.domain.restaurant.events import RestaurantProfileUpdated
from menu_it.domain.restaurant.profile import RestaurantProfile
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.operating_hours import WeeklyOperatingSchedule
from menu_it.domain.value_objects.timezone import TimeZone
from menu_it.infrastructure.repositories.restaurant_profile_repository import (
    SQLAlchemyRestaurantProfileRepository,
)
from menu_it.services.restaurant_profile import (
    UpdateRestaurantProfileCommand,
    UpdateRestaurantProfileService,
)


class MockEventPublisher:
    """In-memory event publisher capturing published domain events for assertions."""

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    async def publish(self, events: list[DomainEvent]) -> None:
        self.published.extend(events)


@pytest.mark.asyncio
async def test_update_profile_service_success(db_session: AsyncSession) -> None:
    # 1. Setup organization and restaurant
    org = Organization(
        name="Service Org", slug=f"service-org-{uuid4().hex[:6]}", status=OrganizationStatus.ACTIVE
    )
    db_session.add(org)
    await db_session.commit()

    rest = Restaurant(
        organization_id=org.id,
        name="Service Rest",
        slug=f"service-rest-{uuid4().hex[:6]}",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add(rest)
    await db_session.commit()

    repo = SQLAlchemyRestaurantProfileRepository(db_session)
    publisher = MockEventPublisher()
    service = UpdateRestaurantProfileService(repository=repo, event_publisher=publisher)

    # 2. Seed initial profile
    profile = RestaurantProfile.create(
        restaurant_id=rest.id,
        organization_id=org.id,
        public_name="Original Name",
        primary_currency=Currency("USD"),
        timezone=TimeZone("America/New_York"),
    )
    await repo.save(profile)
    await db_session.commit()

    # 3. Execute update command
    cmd = UpdateRestaurantProfileCommand(
        restaurant_id=rest.id,
        organization_id=org.id,
        public_name="Updated Bistro",
        legal_name="Bistro Inc",
        description="A great place",
        email="info@bistro.com",
        phone="+14155552671",
        address_line_1="100 Pine St",
        address_locality="San Francisco",
        address_country_code="US",
        primary_currency="EUR",
        timezone="Europe/Paris",
        schedule_payload=WeeklyOperatingSchedule.create_standard(
            opens_at=time(9, 0),
            closes_at=time(21, 0),
        ).to_dict(),
        website_url="https://bistro.com",
    )
    updated = await service.execute(cmd)
    await db_session.commit()

    assert updated.public_name == "Updated Bistro"
    assert updated.legal_name == "Bistro Inc"
    assert updated.primary_currency.code == "EUR"
    assert updated.timezone.name == "Europe/Paris"
    assert updated.address is not None and updated.address.locality == "San Francisco"
    assert updated.email is not None and updated.email.value == "info@bistro.com"
    assert updated.website_url == "https://bistro.com"

    # Verify event publishing
    assert len(publisher.published) > 0
    assert any(isinstance(e, RestaurantProfileUpdated) for e in publisher.published)


@pytest.mark.asyncio
async def test_update_profile_service_nonexistent_raises(db_session: AsyncSession) -> None:
    repo = SQLAlchemyRestaurantProfileRepository(db_session)
    service = UpdateRestaurantProfileService(repository=repo)

    cmd = UpdateRestaurantProfileCommand(
        restaurant_id=uuid4(),
        organization_id=uuid4(),
        public_name="Nonexistent",
    )
    with pytest.raises(EntityNotFoundError, match="not found"):
        await service.execute(cmd)
