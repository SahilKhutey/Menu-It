"""Organization management & onboarding application service (FCD-14 WP-03, WP-09)."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationMembership,
    OrganizationRole,
)
from menu_it.database.models.settings import OrganizationSettings
from menu_it.domain.base.errors import EntityNotFoundError
from menu_it.domain.organization.entities import validate_country_code
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.slug import Slug
from menu_it.domain.value_objects.timezone import TimeZone
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.platform.events.contracts import EventEnvelope
from menu_it.platform.events.publisher import OutboxEventPublisher
from menu_it.services.organization_lifecycle import transition_organization


class OrganizationManagementService:
    """Application service for organization onboarding, profile, settings, and lifecycle."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.outbox = OutboxEventPublisher(session)

    async def create_organization(
        self,
        *,
        name: str,
        slug: str,
        actor_user_id: UUID,
        currency_code: str = "INR",
        timezone: str = "UTC",
        country_code: str = "IN",
        legal_name: str | None = None,
        organization_type: str = "company",
        email: str | None = None,
        phone: str | None = None,
        website: str | None = None,
        correlation_id: str | None = None,
    ) -> tuple[Organization, OrganizationMembership]:
        """Atomically create an organization, owner membership, settings, and outbox event."""
        clean_slug = Slug(slug).value
        clean_currency = Currency(currency_code).code
        clean_tz = TimeZone(timezone).name
        clean_country = validate_country_code(country_code)
        now = datetime.now(UTC)

        existing = await self.session.execute(
            select(Organization.id).where(Organization.slug == clean_slug)
        )
        if existing.scalar_one_or_none() is not None:
            raise ResourceConflictError(f"Organization slug '{clean_slug}' is already taken.")

        org = Organization(
            name=name.strip(),
            slug=clean_slug,
            legal_name=legal_name.strip() if legal_name else None,
            organization_type=organization_type,
            email=email,
            phone=phone,
            website=website,
            country_code=clean_country,
            currency_code=clean_currency,
            timezone=clean_tz,
            status=OrganizationStatus.PROVISIONING,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self.session.add(org)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise ResourceConflictError(
                f"Organization slug '{clean_slug}' is already taken."
            ) from exc

        owner_membership = OrganizationMembership(
            organization_id=org.id,
            user_id=actor_user_id,
            role=OrganizationRole.OWNER,
            status=MembershipStatus.ACTIVE,
            joined_at=now,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self.session.add(owner_membership)

        settings_record = OrganizationSettings(
            organization_id=org.id,
            settings_payload={"default_locale": "en"},
        )
        self.session.add(settings_record)

        transition_organization(org, OrganizationStatus.ACTIVE)

        self.session.add(
            OrganizationAuditEvent(
                organization_id=org.id,
                actor_id=actor_user_id,
                action="organization.created",
                resource_type="organization",
                resource_id=str(org.id),
                correlation_id=correlation_id,
                metadata_={"name": org.name, "slug": org.slug},
            )
        )

        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="organization.created",
                schema_version=1,
                organization_id=org.id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"organization_id": str(org.id), "slug": org.slug},
                occurred_at=now,
            )
        )
        await self.session.flush()
        return org, owner_membership

    async def list_user_organizations(self, user_id: UUID) -> list[Organization]:
        """List all organizations where the user holds an active membership."""
        stmt = (
            select(Organization)
            .join(OrganizationMembership, OrganizationMembership.organization_id == Organization.id)
            .where(
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.status == MembershipStatus.ACTIVE,
            )
            .order_by(Organization.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_organization(self, organization_id: UUID) -> Organization:
        """Fetch organization by ID or raise EntityNotFoundError."""
        result = await self.session.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        org = result.scalar_one_or_none()
        if org is None:
            raise EntityNotFoundError(f"Organization '{organization_id}' not found.")
        return org

    async def update_organization(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        name: str | None = None,
        legal_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        website: str | None = None,
        country_code: str | None = None,
        currency_code: str | None = None,
        timezone: str | None = None,
        correlation_id: str | None = None,
    ) -> Organization:
        """Update organization profile fields and stage audit + outbox event."""
        org = await self.get_organization(organization_id)
        if name is not None:
            org.name = name.strip()
        if legal_name is not None:
            org.legal_name = legal_name.strip() or None
        if email is not None:
            org.email = email
        if phone is not None:
            org.phone = phone
        if website is not None:
            org.website = website
        if country_code is not None:
            org.country_code = validate_country_code(country_code)
        if currency_code is not None:
            org.currency_code = Currency(currency_code).code
        if timezone is not None:
            org.timezone = TimeZone(timezone).name
        org.updated_by = actor_user_id

        self.session.add(
            OrganizationAuditEvent(
                organization_id=org.id,
                actor_id=actor_user_id,
                action="organization.updated",
                resource_type="organization",
                resource_id=str(org.id),
                correlation_id=correlation_id,
                metadata_={"name": org.name},
            )
        )
        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="organization.updated",
                schema_version=1,
                organization_id=org.id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"organization_id": str(org.id)},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return org

    async def get_settings(self, organization_id: UUID) -> OrganizationSettings:
        """Fetch organization settings, creating default record if absent."""
        result = await self.session.execute(
            select(OrganizationSettings).where(
                OrganizationSettings.organization_id == organization_id
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            record = OrganizationSettings(organization_id=organization_id, settings_payload={})
            self.session.add(record)
            await self.session.flush()
        return record

    async def update_settings(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        settings_payload: dict[str, Any],
        correlation_id: str | None = None,
    ) -> OrganizationSettings:
        """Merge and persist organization settings."""
        record = await self.get_settings(organization_id)
        merged = dict(record.settings_payload or {})
        merged.update(settings_payload)
        record.settings_payload = merged

        self.session.add(
            OrganizationAuditEvent(
                organization_id=organization_id,
                actor_id=actor_user_id,
                action="organization.settings.updated",
                resource_type="organization_settings",
                resource_id=str(record.id),
                correlation_id=correlation_id,
                metadata_={"keys": sorted(settings_payload.keys())},
            )
        )
        await self.session.flush()
        return record

    async def suspend_organization(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        correlation_id: str | None = None,
    ) -> Organization:
        """Transition organization to SUSPENDED via FCD-04 lifecycle machine."""
        org = await self.get_organization(organization_id)
        transition_organization(org, OrganizationStatus.SUSPENDED)
        org.updated_by = actor_user_id

        self.session.add(
            OrganizationAuditEvent(
                organization_id=org.id,
                actor_id=actor_user_id,
                action="organization.suspended",
                resource_type="organization",
                resource_id=str(org.id),
                correlation_id=correlation_id,
                metadata_={"status": org.status.value},
            )
        )
        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="organization.suspended",
                schema_version=1,
                organization_id=org.id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"organization_id": str(org.id), "status": org.status.value},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return org
