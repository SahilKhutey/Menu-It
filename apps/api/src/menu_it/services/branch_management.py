"""Branch management & branch assignment application service (FCD-14 WP-05, WP-09)."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.branch import Branch, BranchStatus
from menu_it.database.models.branch_assignment import BranchAssignment, BranchRole
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationMembership,
)
from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.domain.base.errors import BusinessRuleViolationError, EntityNotFoundError
from menu_it.domain.branch.lifecycle import validate_branch_transition
from menu_it.domain.organization.entities import validate_country_code
from menu_it.domain.value_objects.slug import Slug
from menu_it.domain.value_objects.timezone import TimeZone
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.platform.events.contracts import EventEnvelope
from menu_it.platform.events.publisher import OutboxEventPublisher


class BranchManagementService:
    """Application service for restaurant branch CRUD, lifecycle, and staff assignments."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.outbox = OutboxEventPublisher(session)

    async def _require_restaurant(
        self, *, organization_id: UUID, restaurant_id: UUID, require_active: bool = False
    ) -> Restaurant:
        result = await self.session.execute(
            select(Restaurant).where(
                Restaurant.id == restaurant_id,
                Restaurant.organization_id == organization_id,
            )
        )
        restaurant = result.scalar_one_or_none()
        if restaurant is None:
            raise EntityNotFoundError(f"Restaurant '{restaurant_id}' not found.")
        if require_active and restaurant.status != RestaurantStatus.ACTIVE:
            raise BusinessRuleViolationError(
                f"Cannot create branch under restaurant in '{restaurant.status.value}' status."
            )
        return restaurant

    async def create_branch(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        name: str,
        slug: str,
        timezone: str = "UTC",
        country_code: str = "IN",
        branch_code: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        address_line_1: str | None = None,
        address_line_2: str | None = None,
        city: str | None = None,
        state_region: str | None = None,
        postal_code: str | None = None,
        latitude: Decimal | None = None,
        longitude: Decimal | None = None,
        correlation_id: str | None = None,
    ) -> Branch:
        """Create a physical branch under an active restaurant within the same organization."""
        await self._require_restaurant(
            organization_id=organization_id, restaurant_id=restaurant_id, require_active=True
        )
        clean_slug = Slug(slug).value
        clean_tz = TimeZone(timezone).name
        clean_country = validate_country_code(country_code)

        existing = await self.session.execute(
            select(Branch.id).where(
                Branch.restaurant_id == restaurant_id,
                Branch.slug == clean_slug,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ResourceConflictError(
                f"Branch slug '{clean_slug}' already exists in this restaurant."
            )

        branch = Branch(
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            name=name.strip(),
            slug=clean_slug,
            branch_code=branch_code,
            email=email,
            phone=phone,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state_region=state_region,
            postal_code=postal_code,
            country_code=clean_country,
            latitude=latitude,
            longitude=longitude,
            timezone=clean_tz,
            status=BranchStatus.ACTIVE,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self.session.add(branch)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise ResourceConflictError(
                "Branch slug or code conflicts with an existing branch."
            ) from exc

        self.session.add(
            OrganizationAuditEvent(
                organization_id=organization_id,
                actor_id=actor_user_id,
                action="branch.created",
                resource_type="branch",
                resource_id=str(branch.id),
                correlation_id=correlation_id,
                metadata_={"restaurant_id": str(restaurant_id), "name": branch.name},
            )
        )
        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="branch.created",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={
                    "restaurant_id": str(restaurant_id),
                    "branch_id": str(branch.id),
                },
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return branch

    async def list_branches(self, *, organization_id: UUID, restaurant_id: UUID) -> list[Branch]:
        """List all branches belonging to a restaurant within the active organization."""
        await self._require_restaurant(organization_id=organization_id, restaurant_id=restaurant_id)
        result = await self.session.execute(
            select(Branch)
            .where(
                Branch.organization_id == organization_id,
                Branch.restaurant_id == restaurant_id,
            )
            .order_by(Branch.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_branch(self, *, organization_id: UUID, branch_id: UUID) -> Branch:
        """Retrieve a branch strictly scoped to organization_id."""
        result = await self.session.execute(
            select(Branch).where(
                Branch.id == branch_id,
                Branch.organization_id == organization_id,
            )
        )
        branch = result.scalar_one_or_none()
        if branch is None:
            raise EntityNotFoundError(f"Branch '{branch_id}' not found.")
        return branch

    async def update_branch(
        self,
        *,
        organization_id: UUID,
        branch_id: UUID,
        actor_user_id: UUID,
        name: str | None = None,
        branch_code: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        address_line_1: str | None = None,
        address_line_2: str | None = None,
        city: str | None = None,
        state_region: str | None = None,
        postal_code: str | None = None,
        country_code: str | None = None,
        timezone: str | None = None,
        correlation_id: str | None = None,
    ) -> Branch:
        """Update branch operational details and address."""
        branch = await self.get_branch(organization_id=organization_id, branch_id=branch_id)
        if name is not None:
            branch.name = name.strip()
        if branch_code is not None:
            branch.branch_code = branch_code
        if email is not None:
            branch.email = email
        if phone is not None:
            branch.phone = phone
        if address_line_1 is not None:
            branch.address_line_1 = address_line_1
        if address_line_2 is not None:
            branch.address_line_2 = address_line_2
        if city is not None:
            branch.city = city
        if state_region is not None:
            branch.state_region = state_region
        if postal_code is not None:
            branch.postal_code = postal_code
        if country_code is not None:
            branch.country_code = validate_country_code(country_code)
        if timezone is not None:
            branch.timezone = TimeZone(timezone).name
        branch.updated_by = actor_user_id

        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="branch.updated",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"branch_id": str(branch.id)},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return branch

    async def transition_status(
        self,
        *,
        organization_id: UUID,
        branch_id: UUID,
        target_status: BranchStatus,
        actor_user_id: UUID,
        correlation_id: str | None = None,
    ) -> Branch:
        """Apply validated branch lifecycle transition."""
        branch = await self.get_branch(organization_id=organization_id, branch_id=branch_id)
        validate_branch_transition(branch.status.value, target_status.value)
        branch.status = target_status
        branch.updated_by = actor_user_id

        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="branch.status.changed",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"branch_id": str(branch.id), "status": branch.status.value},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return branch

    async def list_assignments(
        self, *, organization_id: UUID, branch_id: UUID
    ) -> list[BranchAssignment]:
        """List staff assignments for a branch."""
        await self.get_branch(organization_id=organization_id, branch_id=branch_id)
        result = await self.session.execute(
            select(BranchAssignment).where(
                BranchAssignment.organization_id == organization_id,
                BranchAssignment.branch_id == branch_id,
            )
        )
        return list(result.scalars().all())

    async def upsert_assignment(
        self,
        *,
        organization_id: UUID,
        branch_id: UUID,
        user_id: UUID,
        role: BranchRole,
        actor_user_id: UUID,
        correlation_id: str | None = None,
    ) -> BranchAssignment:
        """Assign a user to a branch after verifying active organization membership."""
        branch = await self.get_branch(organization_id=organization_id, branch_id=branch_id)

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
                "User must hold an active organization membership before branch assignment."
            )

        existing = (
            await self.session.execute(
                select(BranchAssignment).where(
                    BranchAssignment.branch_id == branch_id,
                    BranchAssignment.user_id == user_id,
                )
            )
        ).scalar_one_or_none()

        if existing is not None:
            existing.role = role
            existing.status = MembershipStatus.ACTIVE
            await self.session.flush()
            return existing

        assignment = BranchAssignment(
            organization_id=organization_id,
            restaurant_id=branch.restaurant_id,
            branch_id=branch.id,
            user_id=user_id,
            role=role,
            status=MembershipStatus.ACTIVE,
            created_by=actor_user_id,
        )
        self.session.add(assignment)
        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="branch.assignment.created",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"branch_id": str(branch.id), "user_id": str(user_id)},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return assignment

    async def remove_assignment(
        self,
        *,
        organization_id: UUID,
        branch_id: UUID,
        user_id: UUID,
        actor_user_id: UUID,
        correlation_id: str | None = None,
    ) -> None:
        """Remove a user's assignment from a branch."""
        await self.get_branch(organization_id=organization_id, branch_id=branch_id)
        existing = (
            await self.session.execute(
                select(BranchAssignment).where(
                    BranchAssignment.organization_id == organization_id,
                    BranchAssignment.branch_id == branch_id,
                    BranchAssignment.user_id == user_id,
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            raise EntityNotFoundError("Branch assignment not found.")
        await self.session.delete(existing)
        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="branch.assignment.removed",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"branch_id": str(branch_id), "user_id": str(user_id)},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
