"""Restaurant profile aggregate root (FCD-06 §6.3, §8.5)."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from menu_it.domain.base.aggregate import AggregateRoot
from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.restaurant.events import (
    RestaurantOperatingHoursUpdated,
    RestaurantProfileUpdated,
)
from menu_it.domain.value_objects.address import Address
from menu_it.domain.value_objects.contact import EmailAddress
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.operating_hours import WeeklyOperatingSchedule
from menu_it.domain.value_objects.phone_number import PhoneNumber
from menu_it.domain.value_objects.timezone import TimeZone


@dataclass(eq=False)
class RestaurantProfile(AggregateRoot):
    """Aggregate root managing business profile, contact, address and operating schedule."""

    restaurant_id: UUID
    organization_id: UUID
    public_name: str
    primary_currency: Currency
    timezone: TimeZone
    legal_name: str | None = None
    description: str | None = None
    email: EmailAddress | None = None
    phone: PhoneNumber | None = None
    address: Address | None = None
    schedule: WeeklyOperatingSchedule | None = None
    website_url: str | None = None
    logo_asset_id: UUID | None = None
    banner_asset_id: UUID | None = None
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.public_name or not self.public_name.strip():
            raise ValidationDomainError("Restaurant public name cannot be empty.")
        object.__setattr__(self, "public_name", self.public_name.strip())

        if not isinstance(self.primary_currency, Currency):
            raise ValidationDomainError("primary_currency must be an instance of Currency.")

        if not isinstance(self.timezone, TimeZone):
            raise ValidationDomainError("timezone must be an instance of TimeZone.")

        if self.version < 1:
            raise ValidationDomainError("Profile version must be greater than or equal to 1.")

    @classmethod
    def create(
        cls,
        restaurant_id: UUID,
        organization_id: UUID,
        public_name: str,
        primary_currency: Currency,
        timezone: TimeZone,
        legal_name: str | None = None,
        description: str | None = None,
        email: EmailAddress | None = None,
        phone: PhoneNumber | None = None,
        address: Address | None = None,
        schedule: WeeklyOperatingSchedule | None = None,
        website_url: str | None = None,
        logo_asset_id: UUID | None = None,
        banner_asset_id: UUID | None = None,
        profile_id: UUID | None = None,
    ) -> "RestaurantProfile":
        """Factory method to create a new RestaurantProfile aggregate."""
        pid = profile_id or uuid4()
        now = datetime.now(UTC)
        profile = cls(
            id=pid,
            restaurant_id=restaurant_id,
            organization_id=organization_id,
            public_name=public_name,
            primary_currency=primary_currency,
            timezone=timezone,
            legal_name=legal_name,
            description=description,
            email=email,
            phone=phone,
            address=address,
            schedule=schedule,
            website_url=website_url,
            logo_asset_id=logo_asset_id,
            banner_asset_id=banner_asset_id,
            version=1,
            created_at=now,
            updated_at=now,
        )
        profile.record_event(
            RestaurantProfileUpdated(
                profile_id=pid,
                restaurant_id=restaurant_id,
                organization_id=organization_id,
                changed_fields=("__created__",),
                version=1,
            )
        )
        return profile

    def _apply_mutation(self, changed_fields: tuple[str, ...]) -> None:
        """Advance aggregate version and update timestamp."""
        self.version += 1
        self.updated_at = datetime.now(UTC)
        self.record_event(
            RestaurantProfileUpdated(
                profile_id=self.id,
                restaurant_id=self.restaurant_id,
                organization_id=self.organization_id,
                changed_fields=changed_fields,
                version=self.version,
            )
        )

    def update_public_name(self, new_name: str) -> None:
        """Update public customer-facing name."""
        if not new_name or not new_name.strip():
            raise ValidationDomainError("Restaurant public name cannot be empty.")
        clean_name = new_name.strip()
        if self.public_name != clean_name:
            self.public_name = clean_name
            self._apply_mutation(("public_name",))

    def update_legal_name(self, new_legal_name: str | None) -> None:
        """Update corporate/legal entity name."""
        clean = new_legal_name.strip() if new_legal_name else None
        if self.legal_name != clean:
            self.legal_name = clean
            self._apply_mutation(("legal_name",))

    def update_description(self, new_description: str | None) -> None:
        """Update marketing bio/description."""
        clean = new_description.strip() if new_description else None
        if self.description != clean:
            self.description = clean
            self._apply_mutation(("description",))

    def update_contact(
        self,
        email: EmailAddress | None,
        phone: PhoneNumber | None,
    ) -> None:
        """Update restaurant contact points."""
        changed: list[str] = []
        if self.email != email:
            self.email = email
            changed.append("email")
        if self.phone != phone:
            self.phone = phone
            changed.append("phone")
        if changed:
            self._apply_mutation(tuple(changed))

    def update_address(self, address: Address | None) -> None:
        """Update physical location address."""
        if self.address != address:
            self.address = address
            self._apply_mutation(("address",))

    def update_localization(self, currency: Currency, timezone: TimeZone) -> None:
        """Update restaurant primary currency and operating timezone."""
        if not isinstance(currency, Currency):
            raise ValidationDomainError("currency must be an instance of Currency.")
        if not isinstance(timezone, TimeZone):
            raise ValidationDomainError("timezone must be an instance of TimeZone.")

        changed: list[str] = []
        if self.primary_currency != currency:
            self.primary_currency = currency
            changed.append("primary_currency")
        if self.timezone != timezone:
            self.timezone = timezone
            changed.append("timezone")
        if changed:
            self._apply_mutation(tuple(changed))

    def update_website_url(self, website_url: str | None) -> None:
        """Update restaurant web link."""
        clean = website_url.strip() if website_url else None
        if self.website_url != clean:
            self.website_url = clean
            self._apply_mutation(("website_url",))

    def update_media(
        self,
        logo_asset_id: UUID | None,
        banner_asset_id: UUID | None,
    ) -> None:
        """Update media asset references."""
        changed: list[str] = []
        if self.logo_asset_id != logo_asset_id:
            self.logo_asset_id = logo_asset_id
            changed.append("logo_asset_id")
        if self.banner_asset_id != banner_asset_id:
            self.banner_asset_id = banner_asset_id
            changed.append("banner_asset_id")
        if changed:
            self._apply_mutation(tuple(changed))

    def update_schedule(self, new_schedule: WeeklyOperatingSchedule | None) -> None:
        """Update operating schedule and emit specialized event."""
        if self.schedule != new_schedule:
            self.schedule = new_schedule
            self.version += 1
            self.updated_at = datetime.now(UTC)
            self.record_event(
                RestaurantOperatingHoursUpdated(
                    profile_id=self.id,
                    restaurant_id=self.restaurant_id,
                    organization_id=self.organization_id,
                    version=self.version,
                )
            )
            self.record_event(
                RestaurantProfileUpdated(
                    profile_id=self.id,
                    restaurant_id=self.restaurant_id,
                    organization_id=self.organization_id,
                    changed_fields=("schedule",),
                    version=self.version,
                )
            )
