"""Integration tests for atomic transaction management and rollback (FCD-03 §15.7 & §19.3)."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.restaurant import Restaurant
from menu_it.database.models.tenant import Tenant
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.services.tenant_service import TenantService


@pytest.mark.asyncio
async def test_create_tenant_with_restaurant_success(db_session: AsyncSession):
    """Verify atomic transaction creates both tenant and restaurant on success."""
    service = TenantService(db_session)

    tenant, restaurant = await service.create_tenant_with_restaurant(
        tenant_name="Gourmet Holdings",
        tenant_slug="gourmet-holdings",
        restaurant_name="Gourmet Main",
        restaurant_slug="main-branch",
        timezone="America/Chicago",
    )

    assert tenant.id is not None
    assert restaurant.id is not None
    assert restaurant.tenant_id == tenant.id

    # Verify both records are committed and accessible in the database
    t_result = await db_session.execute(select(Tenant).where(Tenant.slug == "gourmet-holdings"))
    persisted_tenant = t_result.scalar_one_or_none()
    assert persisted_tenant is not None

    r_result = await db_session.execute(
        select(Restaurant).where(
            Restaurant.tenant_id == tenant.id,
            Restaurant.slug == "main-branch",
        )
    )
    persisted_restaurant = r_result.scalar_one_or_none()
    assert persisted_restaurant is not None


@pytest.mark.asyncio
async def test_failed_operation_rolls_back_atomically(db_session: AsyncSession):
    """Verify failed multi-repository operation rolls back completely with zero orphaned records.

    Follows FCD-03 §19.3 deterministic rollback pattern:
    1. Pre-create an existing tenant with slug 'conflict-slug'.
    2. Attempt to create a tenant with the same slug and a new restaurant 'failed-restaurant'.
    3. Assert ResourceConflictError is raised.
    4. Assert no new tenant was inserted.
    5. Assert no restaurant 'failed-restaurant' was persisted.
    """
    # 1. Pre-create baseline tenant
    baseline_tenant = Tenant(
        name="Original Tenant",
        slug="conflict-slug",
    )
    db_session.add(baseline_tenant)
    await db_session.commit()

    service = TenantService(db_session)

    # 2. Attempt operation that must fail due to conflicting slug
    with pytest.raises(ResourceConflictError) as exc_info:
        await service.create_tenant_with_restaurant(
            tenant_name="Conflicting Tenant Attempt",
            tenant_slug="conflict-slug",
            restaurant_name="Failed Restaurant",
            restaurant_slug="failed-restaurant",
        )

    assert "already registered" in str(exc_info.value) or "conflict" in str(exc_info.value)

    # 3. Verify database state remains unpolluted
    tenants_result = await db_session.execute(select(Tenant).where(Tenant.slug == "conflict-slug"))
    all_matching_tenants = list(tenants_result.scalars().all())
    assert len(all_matching_tenants) == 1
    assert all_matching_tenants[0].name == "Original Tenant"

    # 4. Verify no orphaned restaurant was inserted
    restaurants_result = await db_session.execute(
        select(Restaurant).where(Restaurant.slug == "failed-restaurant")
    )
    orphaned_restaurants = list(restaurants_result.scalars().all())
    assert len(orphaned_restaurants) == 0
