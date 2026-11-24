"""Integration tests for foundational ORM models and constraints (FCD-03 §15.5)."""

from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.database.models.tenant import Tenant, TenantStatus


@pytest.mark.asyncio
async def test_create_tenant(db_session: AsyncSession):
    """Verify tenant model persistence with UUID and default timestamps."""
    tenant = Tenant(
        name="Demo Hospitality Group",
        slug="demo-hospitality-group",
        status=TenantStatus.ACTIVE,
    )
    db_session.add(tenant)
    await db_session.commit()

    assert tenant.id is not None
    assert isinstance(tenant.id, UUID)
    assert tenant.name == "Demo Hospitality Group"
    assert tenant.slug == "demo-hospitality-group"
    assert tenant.status == TenantStatus.ACTIVE
    assert tenant.created_at is not None
    assert tenant.updated_at is not None


@pytest.mark.asyncio
async def test_restaurant_requires_valid_tenant(db_session: AsyncSession):
    """Verify foreign key constraint rejects restaurant with nonexistent tenant."""
    nonexistent_tenant_id = UUID("00000000-0000-0000-0000-000000000001")
    restaurant = Restaurant(
        tenant_id=nonexistent_tenant_id,
        name="Orphan Bistro",
        slug="orphan-bistro",
    )
    db_session.add(restaurant)

    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_tenant_slug_uniqueness(db_session: AsyncSession):
    """Verify unique constraint rejects duplicate tenant slug."""
    tenant_1 = Tenant(name="Alpha Group", slug="unique-slug-test")
    db_session.add(tenant_1)
    await db_session.commit()

    tenant_2 = Tenant(name="Beta Group", slug="unique-slug-test")
    db_session.add(tenant_2)

    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_restaurant_slug_unique_per_tenant(db_session: AsyncSession):
    """Verify composite uniqueness of (tenant_id, slug) for restaurants."""
    tenant_a = Tenant(name="Tenant A", slug="tenant-a-test")
    tenant_b = Tenant(name="Tenant B", slug="tenant-b-test")
    db_session.add_all([tenant_a, tenant_b])
    await db_session.commit()

    tenant_a_id = tenant_a.id
    tenant_b_id = tenant_b.id

    # Same tenant duplicate restaurant slug -> must fail
    r1 = Restaurant(tenant_id=tenant_a_id, name="Downtown Bistro", slug="downtown")
    db_session.add(r1)
    await db_session.commit()

    r2_dup = Restaurant(tenant_id=tenant_a_id, name="Downtown Cafe", slug="downtown")
    db_session.add(r2_dup)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    # Different tenant same restaurant slug -> must succeed
    r3_diff_tenant = Restaurant(
        tenant_id=tenant_b_id,
        name="Downtown Bistro B",
        slug="downtown",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add(r3_diff_tenant)
    await db_session.commit()

    assert r3_diff_tenant.id is not None
    assert r3_diff_tenant.slug == "downtown"


@pytest.mark.asyncio
async def test_tenant_deletion_restricted_when_restaurant_exists(db_session: AsyncSession):
    """Verify ondelete=RESTRICT foreign key prevents tenant deletion when restaurants exist."""
    tenant = Tenant(name="Protected Tenant", slug="protected-tenant")
    db_session.add(tenant)
    await db_session.commit()

    restaurant = Restaurant(
        tenant_id=tenant.id,
        name="Protected Branch",
        slug="protected-branch",
    )
    db_session.add(restaurant)
    await db_session.commit()

    # Attempt to delete the tenant while restaurant exists
    await db_session.delete(tenant)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()
