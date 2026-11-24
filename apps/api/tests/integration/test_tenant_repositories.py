"""Integration tests for TenantScopedRepository (FCD-04 §11, §18.4)."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.organization import (
    Organization,
    OrganizationStatus,
)
from menu_it.database.models.restaurant import (
    Restaurant,
    RestaurantStatus,
)
from menu_it.repositories.tenant_restaurants import TenantRestaurantRepository
from menu_it.tenancy.context import TenantContext


@pytest.mark.asyncio
async def test_tenant_a_cannot_read_tenant_b_restaurant(db_session: AsyncSession):
    """Verify Org A repository cannot retrieve Org B restaurant by ID."""
    org_a = Organization(name="Repo Org A", slug="repo-org-a", status=OrganizationStatus.ACTIVE)
    org_b = Organization(name="Repo Org B", slug="repo-org-b", status=OrganizationStatus.ACTIVE)
    db_session.add_all([org_a, org_b])
    await db_session.commit()

    rest_b = Restaurant(
        organization_id=org_b.id,
        name="Branch B",
        slug="branch-b-repo",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add(rest_b)
    await db_session.commit()

    context_a = TenantContext(
        organization_id=org_a.id,
        user_id=uuid4(),
        organization_role="owner",
    )
    repo_a = TenantRestaurantRepository(db_session, context_a)

    result = await repo_a.get_by_id(rest_b.id)
    assert result is None


@pytest.mark.asyncio
async def test_tenant_a_lists_only_own_restaurants(db_session: AsyncSession):
    """Verify list_restaurants is strictly scoped to the context organization."""
    org_a = Organization(name="List Org A", slug="list-org-a", status=OrganizationStatus.ACTIVE)
    org_b = Organization(name="List Org B", slug="list-org-b", status=OrganizationStatus.ACTIVE)
    db_session.add_all([org_a, org_b])
    await db_session.commit()

    r_a1 = Restaurant(
        organization_id=org_a.id, name="A1", slug="a1", status=RestaurantStatus.ACTIVE
    )
    r_a2 = Restaurant(
        organization_id=org_a.id, name="A2", slug="a2", status=RestaurantStatus.ACTIVE
    )
    r_b1 = Restaurant(
        organization_id=org_b.id, name="B1", slug="b1", status=RestaurantStatus.ACTIVE
    )
    db_session.add_all([r_a1, r_a2, r_b1])
    await db_session.commit()

    context_a = TenantContext(
        organization_id=org_a.id,
        user_id=uuid4(),
        organization_role="owner",
    )
    repo_a = TenantRestaurantRepository(db_session, context_a)

    restaurants = await repo_a.list_restaurants()
    assert len(restaurants) == 2
    for r in restaurants:
        assert r.organization_id == org_a.id


@pytest.mark.asyncio
async def test_tenant_cross_mutation_rejected(db_session: AsyncSession):
    """Verify update and delete reject entities belonging to another organization."""
    org_a = Organization(name="Mut Org A", slug="mut-org-a", status=OrganizationStatus.ACTIVE)
    org_b = Organization(name="Mut Org B", slug="mut-org-b", status=OrganizationStatus.ACTIVE)
    db_session.add_all([org_a, org_b])
    await db_session.commit()

    rest_b = Restaurant(
        organization_id=org_b.id,
        name="Branch B Mut",
        slug="branch-b-mut",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add(rest_b)
    await db_session.commit()

    context_a = TenantContext(
        organization_id=org_a.id,
        user_id=uuid4(),
        organization_role="owner",
    )
    repo_a = TenantRestaurantRepository(db_session, context_a)

    with pytest.raises(ValueError) as exc_update:
        await repo_a.update(rest_b)
    assert "Cannot update" in str(exc_update.value)

    with pytest.raises(ValueError) as exc_delete:
        await repo_a.delete(rest_b)
    assert "Cannot delete" in str(exc_delete.value)


@pytest.mark.asyncio
async def test_create_automatically_assigns_tenant_id(db_session: AsyncSession):
    """Verify repo.create forces organization_id from TenantContext."""
    org_a = Organization(name="Create Org", slug="create-org", status=OrganizationStatus.ACTIVE)
    db_session.add(org_a)
    await db_session.commit()

    context_a = TenantContext(
        organization_id=org_a.id,
        user_id=uuid4(),
        organization_role="owner",
    )
    repo_a = TenantRestaurantRepository(db_session, context_a)

    new_rest = Restaurant(
        organization_id=uuid4(),  # arbitrary placeholder
        name="New Flagship",
        slug="new-flagship",
        status=RestaurantStatus.ACTIVE,
    )
    created = await repo_a.create(new_rest)
    await db_session.commit()

    assert created.organization_id == org_a.id
