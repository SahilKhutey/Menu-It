"""Tenant resolver deriving trusted context from identity & membership (FCD-04 §9.4)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.auth.principal import AuthenticatedPrincipal
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
from menu_it.database.models.restaurant_membership import RestaurantMembership
from menu_it.tenancy.context import TenantContext
from menu_it.tenancy.exceptions import (
    RestaurantAccessDeniedError,
    TenantAccessDeniedError,
    TenantNotFoundError,
    TenantSuspendedError,
)


class TenantResolver:
    """Resolves authenticated principal and organization selection into trusted TenantContext."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def resolve(
        self,
        *,
        principal: AuthenticatedPrincipal,
        organization_id: UUID,
        restaurant_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> TenantContext:
        """Resolve tenant context using server-side database validation.

        Rejects untrusted access attempts:
        - Unauthenticated callers.
        - Nonexistent organizations.
        - Suspended or inactive organizations.
        - Missing, invited, suspended, or revoked user memberships.
        - Nonexistent or cross-tenant restaurants.
        - Unassigned restaurant access for non-admin roles.
        """
        if not principal.is_authenticated:
            raise TenantAccessDeniedError(
                "Unauthenticated principal cannot access tenant resources"
            )

        # 1. Lookup organization
        org_stmt = select(Organization).where(Organization.id == organization_id)
        org_result = await self.session.execute(org_stmt)
        org = org_result.scalar_one_or_none()
        if not org:
            raise TenantNotFoundError(f"Organization '{organization_id}' not found")

        # 2. Check organization status
        if org.status == OrganizationStatus.SUSPENDED:
            raise TenantSuspendedError(f"Organization '{org.name}' is suspended")
        if org.status in (
            OrganizationStatus.PROVISIONING,
            OrganizationStatus.DEACTIVATED,
            OrganizationStatus.OFFBOARDING,
        ):
            raise TenantAccessDeniedError(f"Organization '{org.name}' is not active ({org.status})")

        # 3. Lookup user membership
        membership_stmt = select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == principal.user_id,
        )
        membership_result = await self.session.execute(membership_stmt)
        membership = membership_result.scalar_one_or_none()
        if not membership:
            raise TenantNotFoundError(f"User has no membership in organization '{organization_id}'")

        # 4. Verify membership status
        if membership.status == MembershipStatus.INVITED:
            raise TenantAccessDeniedError("Membership invitation has not been accepted")
        if membership.status == MembershipStatus.SUSPENDED:
            raise TenantAccessDeniedError("User membership in organization is suspended")
        if membership.status == MembershipStatus.REVOKED:
            raise TenantAccessDeniedError("User membership in organization has been revoked")
        if membership.status != MembershipStatus.ACTIVE:
            raise TenantAccessDeniedError(f"Membership status '{membership.status}' is not active")

        # 5. Optional restaurant resolution
        restaurant_role = None
        if restaurant_id:
            rest_stmt = select(Restaurant).where(
                Restaurant.id == restaurant_id,
                Restaurant.organization_id == organization_id,
            )
            rest_result = await self.session.execute(rest_stmt)
            restaurant = rest_result.scalar_one_or_none()
            if not restaurant:
                msg = (
                    f"Restaurant '{restaurant_id}' does not belong "
                    f"to organization '{organization_id}'"
                )
                raise RestaurantAccessDeniedError(msg)
            if restaurant.status != RestaurantStatus.ACTIVE:
                raise RestaurantAccessDeniedError(
                    f"Restaurant '{restaurant.name}' is not active ({restaurant.status})"
                )

            # Organization OWNER or ADMIN has implied restaurant management access
            if membership.role in (OrganizationRole.OWNER, OrganizationRole.ADMIN):
                restaurant_role = "manager"
            else:
                # Check explicit restaurant assignment
                rm_stmt = select(RestaurantMembership).where(
                    RestaurantMembership.restaurant_id == restaurant_id,
                    RestaurantMembership.user_id == principal.user_id,
                    RestaurantMembership.organization_id == organization_id,
                )
                rm_result = await self.session.execute(rm_stmt)
                rm = rm_result.scalar_one_or_none()
                if not rm:
                    raise RestaurantAccessDeniedError(
                        f"User has no assigned access to restaurant '{restaurant_id}'"
                    )
                restaurant_role = str(rm.role)

        return TenantContext(
            organization_id=organization_id,
            user_id=principal.user_id,
            organization_role=str(membership.role),
            restaurant_id=restaurant_id,
            restaurant_role=restaurant_role,
            correlation_id=correlation_id,
        )
