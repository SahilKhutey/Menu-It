"""Restaurant profile application service and commands (FCD-06 §15)."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from menu_it.domain.base.errors import EntityNotFoundError
from menu_it.domain.ports.event_publisher import DomainEventPublisher
from menu_it.domain.ports.repositories import RestaurantProfileRepository
from menu_it.domain.restaurant.ownership import assert_restaurant_belongs_to_organization
from menu_it.domain.restaurant.profile import RestaurantProfile
from menu_it.domain.value_objects.address import Address
from menu_it.domain.value_objects.contact import EmailAddress
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.operating_hours import WeeklyOperatingSchedule
from menu_it.domain.value_objects.phone_number import PhoneNumber
from menu_it.domain.value_objects.timezone import TimeZone


@dataclass(frozen=True, slots=True)
class UpdateRestaurantProfileCommand:
    """Command carrying changes for a restaurant business profile."""

    restaurant_id: UUID
    organization_id: UUID
    public_name: str | None = None
    legal_name: str | None = None
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    address_locality: str | None = None
    address_admin_area: str | None = None
    address_postal_code: str | None = None
    address_country_code: str | None = None
    primary_currency: str | None = None
    timezone: str | None = None
    schedule_payload: list[dict[str, Any]] | None = None
    website_url: str | None = None
    logo_asset_id: UUID | None = None
    banner_asset_id: UUID | None = None


class UpdateRestaurantProfileService:
    """Application use case service coordinating profile update transaction."""

    def __init__(
        self,
        repository: RestaurantProfileRepository,
        event_publisher: DomainEventPublisher | None = None,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    async def execute(
        self,
        command: UpdateRestaurantProfileCommand,
    ) -> RestaurantProfile:
        """Execute profile update within invariant boundary."""
        # 1. Enforce tenant ownership invariant
        assert_restaurant_belongs_to_organization(
            restaurant_org_id=command.organization_id,
            context_org_id=command.organization_id,
        )

        # 2. Retrieve aggregate root
        profile = await self.repository.get_by_restaurant_id(
            restaurant_id=command.restaurant_id,
            organization_id=command.organization_id,
        )
        if profile is None:
            raise EntityNotFoundError(
                f"Restaurant profile for restaurant '{command.restaurant_id}' not found."
            )

        # 3. Apply mutations conditionally
        if command.public_name is not None:
            profile.update_public_name(command.public_name)

        if command.legal_name is not None:
            profile.update_legal_name(command.legal_name)

        if command.description is not None:
            profile.update_description(command.description)

        if command.email is not None or command.phone is not None:
            email_vo = EmailAddress(command.email) if command.email else profile.email
            phone_vo = PhoneNumber(command.phone) if command.phone else profile.phone
            profile.update_contact(email=email_vo, phone=phone_vo)

        if command.address_line_1 is not None:
            addr_vo = Address(
                line_1=command.address_line_1,
                line_2=command.address_line_2,
                locality=command.address_locality or "",
                administrative_area=command.address_admin_area,
                postal_code=command.address_postal_code,
                country_code=command.address_country_code or "US",
            )
            profile.update_address(addr_vo)

        if command.primary_currency is not None or command.timezone is not None:
            curr_vo = (
                Currency(command.primary_currency)
                if command.primary_currency
                else profile.primary_currency
            )
            tz_vo = TimeZone(command.timezone) if command.timezone else profile.timezone
            profile.update_localization(currency=curr_vo, timezone=tz_vo)

        if command.website_url is not None:
            profile.update_website_url(command.website_url)

        if command.logo_asset_id is not None or command.banner_asset_id is not None:
            logo_id = (
                command.logo_asset_id
                if command.logo_asset_id is not None
                else profile.logo_asset_id
            )
            banner_id = (
                command.banner_asset_id
                if command.banner_asset_id is not None
                else profile.banner_asset_id
            )
            profile.update_media(logo_asset_id=logo_id, banner_asset_id=banner_id)

        if command.schedule_payload is not None:
            schedule_vo = WeeklyOperatingSchedule.from_dict(command.schedule_payload)
            profile.update_schedule(schedule_vo)

        # 4. Save aggregate through repository port
        await self.repository.save(profile)

        # 5. Collect and publish domain events
        events = profile.collect_events()
        if self.event_publisher and events:
            await self.event_publisher.publish(events)

        return profile
