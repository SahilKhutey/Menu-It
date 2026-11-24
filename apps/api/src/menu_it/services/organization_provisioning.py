"""Organization provisioning service (FCD-04 §16)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.organization import (
    Organization,
    OrganizationStatus,
)
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationMembership,
    OrganizationRole,
)
from menu_it.database.models.restaurant import (
    Restaurant,
    RestaurantStatus,
)
from menu_it.database.models.restaurant_membership import (
    RestaurantMembership,
    RestaurantRole,
)
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.services.organization_lifecycle import transition_organization


class OrganizationProvisioningService:
    """Coordinates atomic organization provisioning workflows."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def provision_organization(
        self,
        *,
        name: str,
        slug: str,
        owner_user_id: UUID,
        initial_restaurant_name: str | None = None,
        initial_restaurant_slug: str | None = None,
        initial_restaurant_timezone: str = "UTC",
        correlation_id: str | None = None,
    ) -> tuple[Organization, OrganizationMembership, Restaurant | None]:
        """Atomically provision organization, owner membership, and optional initial restaurant.

        Workflow:
        1. Validates slug availability.
        2. Inserts Organization in PROVISIONING state.
        3. Inserts OrganizationMembership with OWNER role.
        4. Optionally inserts initial Restaurant and RestaurantMembership.
        5. Logs OrganizationAuditEvent.
        6. Transitions Organization to ACTIVE state.
        7. Commits atomically within transaction.
        """
        try:
            async with self.session.begin():
                # 1. Uniqueness pre-check
                existing_stmt = select(Organization.id).where(Organization.slug == slug)
                existing = await self.session.execute(existing_stmt)
                if existing.scalar_one_or_none():
                    raise ResourceConflictError(f"Organization slug '{slug}' is already taken.")

                # 2. Create organization in PROVISIONING state
                organization = Organization(
                    name=name,
                    slug=slug,
                    status=OrganizationStatus.PROVISIONING,
                )
                self.session.add(organization)
                await self.session.flush()

                # 3. Create initial owner membership
                owner_membership = OrganizationMembership(
                    organization_id=organization.id,
                    user_id=owner_user_id,
                    role=OrganizationRole.OWNER,
                    status=MembershipStatus.ACTIVE,
                )
                self.session.add(owner_membership)
                await self.session.flush()

                # 4. Optional initial restaurant
                initial_restaurant: Restaurant | None = None
                if initial_restaurant_name and initial_restaurant_slug:
                    initial_restaurant = Restaurant(
                        organization_id=organization.id,
                        name=initial_restaurant_name,
                        slug=initial_restaurant_slug,
                        timezone=initial_restaurant_timezone,
                        status=RestaurantStatus.ACTIVE,
                    )
                    self.session.add(initial_restaurant)
                    await self.session.flush()

                    rest_membership = RestaurantMembership(
                        organization_id=organization.id,
                        restaurant_id=initial_restaurant.id,
                        user_id=owner_user_id,
                        role=RestaurantRole.MANAGER,
                    )
                    self.session.add(rest_membership)
                    await self.session.flush()

                # 5. Create provisioning audit event
                audit_event = OrganizationAuditEvent(
                    organization_id=organization.id,
                    actor_id=owner_user_id,
                    action="organization.provisioned",
                    resource_type="organization",
                    resource_id=str(organization.id),
                    correlation_id=correlation_id,
                    metadata_={
                        "organization_name": name,
                        "organization_slug": slug,
                        "initial_restaurant": initial_restaurant_name,
                    },
                )
                self.session.add(audit_event)

                # 6. Transition organization to ACTIVE state
                transition_organization(organization, OrganizationStatus.ACTIVE)
                await self.session.flush()

                return organization, owner_membership, initial_restaurant
        except IntegrityError as exc:
            raise ResourceConflictError(
                "A database uniqueness or integrity constraint was violated "
                "during organization provisioning."
            ) from exc
