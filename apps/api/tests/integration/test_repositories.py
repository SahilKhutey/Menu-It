"""Integration tests for repositories (FCD-03 §15.6)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.database.models.tenant import Tenant
from menu_it.repositories.restaurants import RestaurantRepository
from menu_it.repositories.tenants import TenantRepository


@pytest.mark.asyncio
async def test_get_tenant_by_slug(db_session: AsyncSession):
    """Verify TenantRepository retrieves existing tenant by slug."""
    tenant = Tenant(
        name="Restaurant Group LLC",
        slug="restaurant-group-repo",
    )
    db_session.add(tenant)
    await db_session.commit()

    repo = TenantRepository(db_session)
    result = await repo.get_by_slug("restaurant-group-repo")

    assert result is not None
    assert result.id == tenant.id
    assert result.name == "Restaurant Group LLC"


@pytest.mark.asyncio
async def test_missing_tenant_returns_none(db_session: AsyncSession):
    """Verify TenantRepository returns None when slug does not exist."""
    repo = TenantRepository(db_session)
    result = await repo.get_by_slug("nonexistent-slug")
    assert result is None


@pytest.mark.asyncio
async def test_tenant_slug_exists(db_session: AsyncSession):
    """Verify slug_exists correctly identifies existing and nonexistent slugs."""
    tenant = Tenant(name="Presence Check", slug="presence-check-slug")
    db_session.add(tenant)
    await db_session.commit()

    repo = TenantRepository(db_session)
    assert await repo.slug_exists("presence-check-slug") is True
    assert await repo.slug_exists("absent-check-slug") is False


@pytest.mark.asyncio
async def test_restaurant_repository_crud_and_filtering(db_session: AsyncSession):
    """Verify RestaurantRepository CRUD, tenant-scoped filtering, and pagination."""
    tenant = Tenant(name="Multi Branch Group", slug="multi-branch-group")
    db_session.add(tenant)
    await db_session.commit()

    repo = RestaurantRepository(db_session)

    # 1. Create restaurant
    restaurant = Restaurant(
        tenant_id=tenant.id,
        name="Branch Uptown",
        slug="uptown",
        timezone="America/New_York",
        status=RestaurantStatus.ACTIVE,
    )
    created = await repo.create(restaurant)
    await db_session.commit()
    assert created.id is not None

    # 2. Retrieve by tenant and slug
    fetched = await repo.get_by_tenant_and_slug(tenant.id, "uptown")
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.timezone == "America/New_York"

    # 3. Slug exists for tenant
    assert await repo.slug_exists_for_tenant(tenant.id, "uptown") is True
    assert await repo.slug_exists_for_tenant(tenant.id, "nonexistent") is False

    # 4. List by tenant and pagination
    r2 = Restaurant(
        tenant_id=tenant.id,
        name="Branch Midtown",
        slug="midtown",
    )
    await repo.create(r2)
    await db_session.commit()

    branches = await repo.list_by_tenant(tenant.id, offset=0, limit=10)
    assert len(branches) == 2

    page_1 = await repo.list_by_tenant(tenant.id, offset=0, limit=1)
    assert len(page_1) == 1

    # 5. Update
    created.name = "Branch Uptown Flagship"
    updated = await repo.update(created)
    await db_session.commit()
    assert updated.name == "Branch Uptown Flagship"

    # 6. Delete
    await repo.delete(r2)
    await db_session.commit()
    remaining = await repo.list_by_tenant(tenant.id)
    assert len(remaining) == 1
    assert remaining[0].slug == "uptown"
