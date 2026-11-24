"""Domain-to-persistence mapping for RestaurantProfile (FCD-06 §14.2)."""

from menu_it.database.models.restaurant_profile import RestaurantProfileRecord
from menu_it.domain.restaurant.profile import RestaurantProfile
from menu_it.domain.value_objects.address import Address
from menu_it.domain.value_objects.contact import EmailAddress
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.operating_hours import WeeklyOperatingSchedule
from menu_it.domain.value_objects.phone_number import PhoneNumber
from menu_it.domain.value_objects.timezone import TimeZone


class RestaurantProfileMapper:
    """Bi-directional mapper between RestaurantProfile aggregate and database record."""

    @staticmethod
    def to_domain(record: RestaurantProfileRecord) -> RestaurantProfile:
        """Convert database record to pure domain aggregate root."""
        address: Address | None = None
        if record.address_line_1 and record.address_locality and record.address_country_code:
            address = Address(
                line_1=record.address_line_1,
                line_2=record.address_line_2,
                locality=record.address_locality,
                administrative_area=record.address_admin_area,
                postal_code=record.address_postal_code,
                country_code=record.address_country_code,
            )

        email = EmailAddress(record.email) if record.email else None
        phone = PhoneNumber(record.phone) if record.phone else None
        schedule = (
            WeeklyOperatingSchedule.from_dict(record.schedule_payload)
            if record.schedule_payload
            else None
        )

        return RestaurantProfile(
            id=record.id,
            restaurant_id=record.restaurant_id,
            organization_id=record.organization_id,
            public_name=record.public_name,
            primary_currency=Currency(record.primary_currency),
            timezone=TimeZone(record.timezone),
            legal_name=record.legal_name,
            description=record.description,
            email=email,
            phone=phone,
            address=address,
            schedule=schedule,
            website_url=record.website_url,
            logo_asset_id=record.logo_asset_id,
            banner_asset_id=record.banner_asset_id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    @staticmethod
    def to_record(
        domain: RestaurantProfile,
        existing_record: RestaurantProfileRecord | None = None,
    ) -> RestaurantProfileRecord:
        """Convert or update database record from domain aggregate root."""
        record = existing_record or RestaurantProfileRecord(
            id=domain.id,
            restaurant_id=domain.restaurant_id,
            organization_id=domain.organization_id,
            created_at=domain.created_at,
        )

        record.public_name = domain.public_name
        record.legal_name = domain.legal_name
        record.description = domain.description
        record.email = domain.email.value if domain.email else None
        record.phone = domain.phone.e164 if domain.phone else None

        if domain.address:
            record.address_line_1 = domain.address.line_1
            record.address_line_2 = domain.address.line_2
            record.address_locality = domain.address.locality
            record.address_admin_area = domain.address.administrative_area
            record.address_postal_code = domain.address.postal_code
            record.address_country_code = domain.address.country_code
        else:
            record.address_line_1 = None
            record.address_line_2 = None
            record.address_locality = None
            record.address_admin_area = None
            record.address_postal_code = None
            record.address_country_code = None

        record.primary_currency = domain.primary_currency.code
        record.timezone = domain.timezone.name
        record.schedule_payload = domain.schedule.to_dict() if domain.schedule else None
        record.website_url = domain.website_url
        record.logo_asset_id = domain.logo_asset_id
        record.banner_asset_id = domain.banner_asset_id
        record.version = domain.version
        record.updated_at = domain.updated_at

        return record
