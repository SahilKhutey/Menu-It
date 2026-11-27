"""FCD-15 Public profile publication and immutable revision service."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.organization import OrganizationStatus
from menu_it.database.models.restaurant import RestaurantStatus
from menu_it.database.models.restaurant_configuration import (
    RestaurantConfigurationRevision,
    RestaurantPublication,
)
from menu_it.domain.base.errors import BusinessRuleViolationError, EntityNotFoundError
from menu_it.domain.restaurant_configuration import PublicationStatus
from menu_it.platform.cache.service import CacheService
from menu_it.platform.events.contracts import EventEnvelope
from menu_it.platform.events.publisher import OutboxEventPublisher
from menu_it.services.restaurant_configuration import RestaurantConfigurationService


class RestaurantPublicationService:
    """Manages public profile publishing, immutable revisions, unpublishing, and rollback."""

    def __init__(self, session: AsyncSession, cache: CacheService | None = None) -> None:
        self.session = session
        self.cache = cache
        self.config_service = RestaurantConfigurationService(session, cache=cache)
        self.outbox = OutboxEventPublisher(session)

    def _build_public_snapshot(
        self,
        *,
        public_slug: str,
        display_name: str,
        short_description: str | None,
        description: str | None,
        cuisine_type: str | None,
        price_range: str | None,
        website_url: str | None,
        public_email: str | None,
        public_phone: str | None,
        social_links: dict[str, Any],
        timezone: str,
        currency_code: str,
        enabled_services: tuple[str, ...],
        branding: dict[str, Any],
        weekly_hours: dict[str, list[dict[str, Any]]],
    ) -> dict[str, Any]:
        """Allowlisted public DTO snapshot — never includes internal IDs or private contacts."""
        return {
            "public_slug": public_slug,
            "display_name": display_name,
            "short_description": short_description,
            "description": description,
            "cuisine_type": cuisine_type,
            "price_range": price_range,
            "website_url": website_url,
            "public_email": public_email,
            "public_phone": public_phone,
            "social_links": social_links,
            "timezone": timezone,
            "currency_code": currency_code,
            "enabled_services": list(enabled_services),
            "branding": branding,
            "weekly_hours": weekly_hours,
        }

    async def publish(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        public_slug: str | None = None,
        change_summary: str | None = None,
        correlation_id: str | None = None,
    ) -> RestaurantPublication:
        org, rest = await self.config_service._require_restaurant(organization_id, restaurant_id)
        if org.status != OrganizationStatus.ACTIVE or rest.status != RestaurantStatus.ACTIVE:
            raise BusinessRuleViolationError(
                "Restaurant and organization must be active before publishing public profile."
            )

        profile = await self.config_service.get_profile(organization_id, restaurant_id)
        effective = await self.config_service.resolve_effective_configuration(
            organization_id=organization_id,
            restaurant_id=restaurant_id,
        )
        if not effective.display_name or not effective.enabled_services:
            raise BusinessRuleViolationError(
                "Restaurant must have a display name and at least one enabled service to publish."
            )

        slug_value = (public_slug or rest.slug).strip().lower()
        branding_dict: dict[str, Any] = {}
        if effective.branding is not None:
            branding_dict = {
                "logo_asset_id": str(effective.branding.logo_asset_id)
                if effective.branding.logo_asset_id
                else None,
                "cover_asset_id": str(effective.branding.cover_asset_id)
                if effective.branding.cover_asset_id
                else None,
                "primary_color": effective.branding.primary_color.normalized()
                if effective.branding.primary_color
                else None,
                "secondary_color": effective.branding.secondary_color.normalized()
                if effective.branding.secondary_color
                else None,
                "accent_color": effective.branding.accent_color.normalized()
                if effective.branding.accent_color
                else None,
                "font_family": effective.branding.font_family,
                "border_radius": effective.branding.border_radius,
            }

        hours_dict = {
            str(day): [
                {
                    "opens_at": iv.opens_at.strftime("%H:%M"),
                    "closes_at": iv.closes_at.strftime("%H:%M"),
                    "closes_next_day": iv.closes_next_day,
                }
                for iv in intervals
            ]
            for day, intervals in effective.weekly_hours.items()
        }

        snapshot = self._build_public_snapshot(
            public_slug=slug_value,
            display_name=effective.display_name,
            short_description=profile.short_description,
            description=profile.description,
            cuisine_type=profile.cuisine_type,
            price_range=profile.price_range,
            website_url=profile.website_url,
            public_email=profile.public_email,
            public_phone=profile.public_phone,
            social_links=dict(profile.social_links or {}),
            timezone=effective.timezone,
            currency_code=effective.currency_code,
            enabled_services=effective.enabled_services,
            branding=branding_dict,
            weekly_hours=hours_dict,
        )

        max_rev_res = await self.session.execute(
            select(
                func.coalesce(func.max(RestaurantConfigurationRevision.revision_number), 0)
            ).where(
                RestaurantConfigurationRevision.organization_id == organization_id,
                RestaurantConfigurationRevision.restaurant_id == restaurant_id,
            )
        )
        next_rev = int(max_rev_res.scalar_one()) + 1

        self.session.add(
            RestaurantConfigurationRevision(
                organization_id=organization_id,
                restaurant_id=restaurant_id,
                revision_number=next_rev,
                snapshot=snapshot,
                created_by=actor_user_id,
                change_summary=change_summary or f"Published revision {next_rev}",
            )
        )

        pub_res = await self.session.execute(
            select(RestaurantPublication).where(
                RestaurantPublication.organization_id == organization_id,
                RestaurantPublication.restaurant_id == restaurant_id,
            )
        )
        pub = pub_res.scalar_one_or_none()
        now = datetime.now(UTC)
        if pub is None:
            pub = RestaurantPublication(
                organization_id=organization_id,
                restaurant_id=restaurant_id,
                public_slug=slug_value,
                status=PublicationStatus.PUBLISHED.value,
                published_revision=next_rev,
                published_snapshot=snapshot,
                published_at=now,
                published_by=actor_user_id,
            )
            self.session.add(pub)
        else:
            pub.public_slug = slug_value
            pub.status = PublicationStatus.PUBLISHED.value
            pub.published_revision = next_rev
            pub.published_snapshot = snapshot
            pub.published_at = now
            pub.published_by = actor_user_id

        await self._emit_publication_event(
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=actor_user_id,
            event_type="restaurant.profile.published",
            payload={"public_slug": slug_value, "revision": next_rev},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return pub

    async def unpublish(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        correlation_id: str | None = None,
    ) -> RestaurantPublication:
        pub_res = await self.session.execute(
            select(RestaurantPublication).where(
                RestaurantPublication.organization_id == organization_id,
                RestaurantPublication.restaurant_id == restaurant_id,
            )
        )
        pub = pub_res.scalar_one_or_none()
        if pub is None:
            raise EntityNotFoundError(
                f"No publication record found for restaurant '{restaurant_id}'."
            )
        pub.status = PublicationStatus.UNPUBLISHED.value
        await self._emit_publication_event(
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=actor_user_id,
            event_type="restaurant.profile.unpublished",
            payload={"public_slug": pub.public_slug},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return pub

    async def restore_revision(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        revision_number: int,
        actor_user_id: UUID,
        correlation_id: str | None = None,
    ) -> RestaurantPublication:
        rev_res = await self.session.execute(
            select(RestaurantConfigurationRevision).where(
                RestaurantConfigurationRevision.organization_id == organization_id,
                RestaurantConfigurationRevision.restaurant_id == restaurant_id,
                RestaurantConfigurationRevision.revision_number == revision_number,
            )
        )
        rev = rev_res.scalar_one_or_none()
        if rev is None:
            raise EntityNotFoundError(f"Configuration revision '{revision_number}' not found.")

        pub_res = await self.session.execute(
            select(RestaurantPublication).where(
                RestaurantPublication.organization_id == organization_id,
                RestaurantPublication.restaurant_id == restaurant_id,
            )
        )
        pub = pub_res.scalar_one_or_none()
        if pub is None:
            raise EntityNotFoundError(
                f"No publication record found for restaurant '{restaurant_id}'."
            )
        pub.status = PublicationStatus.PUBLISHED.value
        pub.published_revision = rev.revision_number
        pub.published_snapshot = dict(rev.snapshot)
        pub.published_at = datetime.now(UTC)
        pub.published_by = actor_user_id

        await self._emit_publication_event(
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            actor_user_id=actor_user_id,
            event_type="restaurant.profile.published",
            payload={"public_slug": pub.public_slug, "restored_revision": revision_number},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return pub

    async def list_publications(
        self, organization_id: UUID, restaurant_id: UUID
    ) -> list[RestaurantConfigurationRevision]:
        await self.config_service._require_restaurant(organization_id, restaurant_id)
        res = await self.session.execute(
            select(RestaurantConfigurationRevision)
            .where(
                RestaurantConfigurationRevision.organization_id == organization_id,
                RestaurantConfigurationRevision.restaurant_id == restaurant_id,
            )
            .order_by(RestaurantConfigurationRevision.revision_number.desc())
        )
        return list(res.scalars().all())

    async def get_public_profile_by_slug(self, public_slug: str) -> dict[str, Any]:
        clean_slug = public_slug.strip().lower()
        res = await self.session.execute(
            select(RestaurantPublication).where(
                RestaurantPublication.public_slug == clean_slug,
                RestaurantPublication.status == PublicationStatus.PUBLISHED.value,
            )
        )
        pub = res.scalar_one_or_none()
        if pub is None or pub.published_snapshot is None:
            raise EntityNotFoundError(f"Public restaurant profile '{public_slug}' not found.")
        return {
            **dict(pub.published_snapshot),
            "published_revision": pub.published_revision,
            "published_at": pub.published_at.isoformat() if pub.published_at else None,
        }

    async def _emit_publication_event(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        event_type: str,
        payload: dict[str, Any],
        correlation_id: str | None = None,
    ) -> None:
        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type=event_type,
                schema_version=1,
                occurred_at=datetime.now(UTC),
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload=payload,
            )
        )
        self.session.add(
            OrganizationAuditEvent(
                organization_id=organization_id,
                actor_id=actor_user_id,
                action=event_type,
                resource_type="restaurant_publication",
                resource_id=str(restaurant_id),
                correlation_id=correlation_id,
                metadata_=payload,
            )
        )
        if self.cache is not None:
            await self.cache.invalidate_organization_resource(organization_id, "restaurant_config")
