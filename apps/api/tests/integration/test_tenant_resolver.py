"""Integration tests for TenantResolver (FCD-04 §9.4, §18.3)."""

from uuid import UUID, uuid4

import pytest
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
from menu_it.database.models.restaurant_membership import (
    RestaurantMembership,
    RestaurantRole,
)
from menu_it.database.models.user import User, UserStatus
from menu_it.tenancy.exceptions import (
    RestaurantAccessDeniedError,
    TenantAccessDeniedError,
    TenantNotFoundError,
    TenantSuspendedError,
)
from menu_it.tenancy.resolver import TenantResolver


async def _create_test_user(
    session: AsyncSession,
    user_id: UUID | None = None,
) -> User:
    uid = user_id or uuid4()
    u = User(
        id=uid,
        email=f"u_{uid}@test.internal",
        normalized_email=f"u_{uid}@test.internal",
        display_name="Test User",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    session.add(u)
    await session.commit()
    return u


@pytest.mark.asyncio
async def test_user_cannot_resolve_unrelated_organization(db_session: AsyncSession):
    """Verify principal without membership receives TenantNotFoundError (never leaks existence)."""
    org = Organization(
        name="Org Alpha",
        slug="org-alpha-res",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org)
    await db_session.commit()

    unrelated_user = uuid4()
    principal = AuthenticatedPrincipal(user_id=unrelated_user)
    resolver = TenantResolver(db_session)

    with pytest.raises(TenantNotFoundError):
        await resolver.resolve(
            principal=principal,
            organization_id=org.id,
        )


@pytest.mark.asyncio
async def test_active_member_resolves_organization(db_session: AsyncSession):
    """Verify active organization member resolves immutable TenantContext."""
    user = await _create_test_user(db_session)
    user_id = user.id
    org = Organization(
        name="Org Beta",
        slug="org-beta-res",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org)
    await db_session.commit()

    membership = OrganizationMembership(
        organization_id=org.id,
        user_id=user_id,
        role=OrganizationRole.ADMIN,
        status=MembershipStatus.ACTIVE,
    )
    db_session.add(membership)
    await db_session.commit()

    principal = AuthenticatedPrincipal(user_id=user_id)
    resolver = TenantResolver(db_session)
    context = await resolver.resolve(
        principal=principal,
        organization_id=org.id,
        correlation_id="corr-xyz",
    )

    assert context.organization_id == org.id
    assert context.user_id == user_id
    assert context.organization_role == "admin"
    assert context.restaurant_id is None
    assert context.correlation_id == "corr-xyz"


@pytest.mark.asyncio
async def test_membership_statuses_rejected(db_session: AsyncSession):
    """Verify invited, suspended, and revoked memberships are all rejected."""
    org = Organization(
        name="Status Check Org",
        slug="status-check-org",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org)
    await db_session.commit()

    resolver = TenantResolver(db_session)

    for status in [
        MembershipStatus.INVITED,
        MembershipStatus.SUSPENDED,
        MembershipStatus.REVOKED,
    ]:
        user = await _create_test_user(db_session)
        user_id = user.id
        mem = OrganizationMembership(
            organization_id=org.id,
            user_id=user_id,
            role=OrganizationRole.STAFF,
            status=status,
        )
        db_session.add(mem)
        await db_session.commit()

        principal = AuthenticatedPrincipal(user_id=user_id)
        with pytest.raises(TenantAccessDeniedError):
            await resolver.resolve(
                principal=principal,
                organization_id=org.id,
            )


@pytest.mark.asyncio
async def test_organization_statuses_enforced(db_session: AsyncSession):
    """Verify suspended org raises TenantSuspendedError, others raise TenantAccessDeniedError."""
    resolver = TenantResolver(db_session)

    # 1. Suspended organization
    user_a_obj = await _create_test_user(db_session)
    user_a = user_a_obj.id
    org_suspended = Organization(
        name="Suspended Org",
        slug="org-suspended-res",
        status=OrganizationStatus.SUSPENDED,
    )
    db_session.add(org_suspended)
    await db_session.commit()

    mem_a = OrganizationMembership(
        organization_id=org_suspended.id,
        user_id=user_a,
        role=OrganizationRole.OWNER,
        status=MembershipStatus.ACTIVE,
    )
    db_session.add(mem_a)
    await db_session.commit()

    with pytest.raises(TenantSuspendedError):
        await resolver.resolve(
            principal=AuthenticatedPrincipal(user_id=user_a),
            organization_id=org_suspended.id,
        )

    # 2. Provisioning organization
    user_b_obj = await _create_test_user(db_session)
    user_b = user_b_obj.id
    org_prov = Organization(
        name="Prov Org",
        slug="org-prov-res",
        status=OrganizationStatus.PROVISIONING,
    )
    db_session.add(org_prov)
    await db_session.commit()

    mem_b = OrganizationMembership(
        organization_id=org_prov.id,
        user_id=user_b,
        role=OrganizationRole.OWNER,
        status=MembershipStatus.ACTIVE,
    )
    db_session.add(mem_b)
    await db_session.commit()

    with pytest.raises(TenantAccessDeniedError):
        await resolver.resolve(
            principal=AuthenticatedPrincipal(user_id=user_b),
            organization_id=org_prov.id,
        )


@pytest.mark.asyncio
async def test_restaurant_resolution_and_scope(db_session: AsyncSession):
    """Verify restaurant scoping: cross-org rejected, unassigned rejected, owner implied access."""
    # Org A with Restaurant A
    org_a = Organization(
        name="Org Scope A",
        slug="org-scope-a",
        status=OrganizationStatus.ACTIVE,
    )
    # Org B with Restaurant B
    org_b = Organization(
        name="Org Scope B",
        slug="org-scope-b",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add_all([org_a, org_b])
    await db_session.commit()

    rest_a = Restaurant(
        organization_id=org_a.id,
        name="Branch A",
        slug="branch-a",
        status=RestaurantStatus.ACTIVE,
    )
    rest_b = Restaurant(
        organization_id=org_b.id,
        name="Branch B",
        slug="branch-b",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add_all([rest_a, rest_b])
    await db_session.commit()

    owner_u = await _create_test_user(db_session)
    staff_u = await _create_test_user(db_session)
    owner_user = owner_u.id
    staff_user = staff_u.id

    db_session.add(
        OrganizationMembership(
            organization_id=org_a.id,
            user_id=owner_user,
            role=OrganizationRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )
    )
    db_session.add(
        OrganizationMembership(
            organization_id=org_a.id,
            user_id=staff_user,
            role=OrganizationRole.STAFF,
            status=MembershipStatus.ACTIVE,
        )
    )
    await db_session.commit()

    resolver = TenantResolver(db_session)

    # 1. Owner has implied access to Restaurant A without explicit restaurant_membership
    owner_ctx = await resolver.resolve(
        principal=AuthenticatedPrincipal(user_id=owner_user),
        organization_id=org_a.id,
        restaurant_id=rest_a.id,
    )
    assert owner_ctx.restaurant_id == rest_a.id
    assert owner_ctx.restaurant_role == "manager"

    # 2. Staff user without restaurant_membership -> rejected
    with pytest.raises(RestaurantAccessDeniedError):
        await resolver.resolve(
            principal=AuthenticatedPrincipal(user_id=staff_user),
            organization_id=org_a.id,
            restaurant_id=rest_a.id,
        )

    # 3. Staff user with restaurant_membership -> succeeds
    db_session.add(
        RestaurantMembership(
            organization_id=org_a.id,
            restaurant_id=rest_a.id,
            user_id=staff_user,
            role=RestaurantRole.STAFF,
        )
    )
    await db_session.commit()

    staff_ctx = await resolver.resolve(
        principal=AuthenticatedPrincipal(user_id=staff_user),
        organization_id=org_a.id,
        restaurant_id=rest_a.id,
    )
    assert staff_ctx.restaurant_id == rest_a.id
    assert staff_ctx.restaurant_role == "staff"

    # 4. Cross-org restaurant access: User accessing Org A with Restaurant B is rejected
    with pytest.raises(RestaurantAccessDeniedError):
        await resolver.resolve(
            principal=AuthenticatedPrincipal(user_id=owner_user),
            organization_id=org_a.id,
            restaurant_id=rest_b.id,
        )
