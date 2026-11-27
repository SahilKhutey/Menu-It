"""Restaurant management application service (FCD-14 WP-04, WP-09)."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationMembership,
)
from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.database.models.restaurant_membership import (
    RestaurantMembership,
    RestaurantRole,
)
from menu_it.database.models.settings import RestaurantSettings
from menu_it.domain.base.errors import BusinessRuleViolationError, EntityNotFoundError
from menu_it.domain.value_objects.slug import Slug
from menu_it.domain.value_objects.timezone import TimeZone
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.platform.events.contracts import EventEnvelope
from menu_it.platform.events.publisher import OutboxEventPublisher
from menu_it.services.restaurant_lifecycle import transition_restaurant


class RestaurantManagementService:
    """Application service for restaurant creation, updates, lifecycle, and memberships."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.outbox = OutboxEventPublisher(session)

    async def _require_active_organization(self, organization_id: UUID) -> Organization:
        result = await self.session.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        org = result.scalar_one_or_none()
        if org is None:
            raise EntityNotFoundError(f"Organization '{organization_id}' not found.")
        if org.status != OrganizationStatus.ACTIVE:
            raise BusinessRuleViolationError(
                f"Cannot modify restaurants while organization is '{org.status.value}'."
            )
        return org

    async def create_restaurant(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        name: str,
        slug: str,
        timezone: str = "UTC",
        description: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        website: str | None = None,
        cuisine_type: str | None = None,
        correlation_id: str | None = None,
    ) -> Restaurant:
        """Create a restaurant within an active organization and stage outbox event."""
        await self._require_active_organization(organization_id)
        clean_slug = Slug(slug).value
        clean_tz = TimeZone(timezone).name

        existing = await self.session.execute(
            select(Restaurant.id).where(
                Restaurant.organization_id == organization_id,
                Restaurant.slug == clean_slug,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ResourceConflictError(
                f"Restaurant slug '{clean_slug}' already exists in this organization."
            )

        restaurant = Restaurant(
            organization_id=organization_id,
            name=name.strip(),
            slug=clean_slug,
            timezone=clean_tz,
            description=description,
            email=email,
            phone=phone,
            website=website,
            cuisine_type=cuisine_type,
            status=RestaurantStatus.ACTIVE,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self.session.add(restaurant)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise ResourceConflictError(
                f"Restaurant slug '{clean_slug}' already exists in this organization."
            ) from exc

        self.session.add(
            RestaurantSettings(
                organization_id=organization_id,
                restaurant_id=restaurant.id,
                settings_payload={},
            )
        )

        self.session.add(
            OrganizationAuditEvent(
                organization_id=organization_id,
                actor_id=actor_user_id,
                action="restaurant.created",
                resource_type="restaurant",
                resource_id=str(restaurant.id),
                correlation_id=correlation_id,
                metadata_={"name": restaurant.name, "slug": restaurant.slug},
            )
        )

        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="restaurant.created",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"restaurant_id": str(restaurant.id), "slug": restaurant.slug},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return restaurant

    async def list_restaurants(
        self,
        *,
        organization_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Restaurant], int]:
        """List paginated restaurants scoped strictly to organization_id."""
        stmt = (
            select(Restaurant)
            .where(Restaurant.organization_id == organization_id)
            .order_by(Restaurant.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        items = list((await self.session.execute(stmt)).scalars().all())
        count_stmt = (
            select(func.count())
            .select_from(Restaurant)
            .where(Restaurant.organization_id == organization_id)
        )
        total = int((await self.session.execute(count_stmt)).scalar_one())
        return items, total

    async def get_restaurant(self, *, organization_id: UUID, restaurant_id: UUID) -> Restaurant:
        """Retrieve a restaurant strictly scoped to organization_id."""
        result = await self.session.execute(
            select(Restaurant).where(
                Restaurant.id == restaurant_id,
                Restaurant.organization_id == organization_id,
            )
        )
        restaurant = result.scalar_one_or_none()
        if restaurant is None:
            raise EntityNotFoundError(f"Restaurant '{restaurant_id}' not found.")
        return restaurant

    async def update_restaurant(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        name: str | None = None,
        description: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        website: str | None = None,
        cuisine_type: str | None = None,
        timezone: str | None = None,
        correlation_id: str | None = None,
    ) -> Restaurant:
        """Update restaurant profile fields."""
        restaurant = await self.get_restaurant(
            organization_id=organization_id, restaurant_id=restaurant_id
        )
        if name is not None:
            restaurant.name = name.strip()
        if description is not None:
            restaurant.description = description
        if email is not None:
            restaurant.email = email
        if phone is not None:
            restaurant.phone = phone
        if website is not None:
            restaurant.website = website
        if cuisine_type is not None:
            restaurant.cuisine_type = cuisine_type
        if timezone is not None:
            restaurant.timezone = TimeZone(timezone).name
        restaurant.updated_by = actor_user_id

        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="restaurant.updated",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"restaurant_id": str(restaurant.id)},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return restaurant

    async def transition_status(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        target_status: RestaurantStatus,
        actor_user_id: UUID,
        correlation_id: str | None = None,
    ) -> Restaurant:
        """Apply canonical FCD-04 restaurant lifecycle transition."""
        restaurant = await self.get_restaurant(
            organization_id=organization_id, restaurant_id=restaurant_id
        )
        transition_restaurant(restaurant, target_status)
        restaurant.updated_by = actor_user_id

        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="restaurant.status.changed",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"restaurant_id": str(restaurant.id), "status": restaurant.status.value},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return restaurant

    async def get_settings(
        self, *, organization_id: UUID, restaurant_id: UUID
    ) -> RestaurantSettings:
        """Retrieve restaurant settings scoped to tenant."""
        await self.get_restaurant(organization_id=organization_id, restaurant_id=restaurant_id)
        result = await self.session.execute(
            select(RestaurantSettings).where(
                RestaurantSettings.organization_id == organization_id,
                RestaurantSettings.restaurant_id == restaurant_id,
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            record = RestaurantSettings(
                organization_id=organization_id,
                restaurant_id=restaurant_id,
                settings_payload={},
            )
            self.session.add(record)
            await self.session.flush()
        return record

    async def update_settings(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        settings_payload: dict[str, Any],
    ) -> RestaurantSettings:
        """Update restaurant settings payload."""
        record = await self.get_settings(
            organization_id=organization_id, restaurant_id=restaurant_id
        )
        merged = dict(record.settings_payload or {})
        merged.update(settings_payload)
        record.settings_payload = merged
        await self.session.flush()
        return record

    async def list_members(
        self, *, organization_id: UUID, restaurant_id: UUID
    ) -> list[RestaurantMembership]:
        """List restaurant-scoped memberships."""
        await self.get_restaurant(organization_id=organization_id, restaurant_id=restaurant_id)
        result = await self.session.execute(
            select(RestaurantMembership).where(
                RestaurantMembership.organization_id == organization_id,
                RestaurantMembership.restaurant_id == restaurant_id,
            )
        )
        return list(result.scalars().all())

    async def assign_member(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        user_id: UUID,
        role: RestaurantRole,
    ) -> RestaurantMembership:
        """Assign or update a restaurant membership after verifying active org membership."""
        await self.get_restaurant(organization_id=organization_id, restaurant_id=restaurant_id)

        org_member = (
            await self.session.execute(
                select(OrganizationMembership).where(
                    OrganizationMembership.organization_id == organization_id,
                    OrganizationMembership.user_id == user_id,
                    OrganizationMembership.status == MembershipStatus.ACTIVE,
                )
            )
        ).scalar_one_or_none()
        if org_member is None:
            raise BusinessRuleViolationError(
                "User must hold an active organization membership before restaurant assignment."
            )

        existing = (
            await self.session.execute(
                select(RestaurantMembership).where(
                    RestaurantMembership.restaurant_id == restaurant_id,
                    RestaurantMembership.user_id == user_id,
                )
            )
        ).scalar_one_or_none()

        if existing is not None:
            existing.role = role
            await self.session.flush()
            return existing

        membership = RestaurantMembership(
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            user_id=user_id,
            role=role,
        )
        self.session.add(membership)
        await self.session.flush()
        return membership
