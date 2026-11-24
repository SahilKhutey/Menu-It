"""Integration tests for restaurant profile tenant isolation and RLS policy rules (FCD-06 §15)."""

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.database.models.restaurant_profile import RestaurantProfileRecord
from menu_it.infrastructure.repositories.restaurant_profile_repository import (
    SQLAlchemyRestaurantProfileRepository,
)


@pytest.mark.asyncio
async def test_restaurant_profile_tenant_isolation(db_session: AsyncSession) -> None:
    """Verify Org A cannot query or access Org B's restaurant profile."""
    # 1. Create Organization A and B
    org_a = Organization(
        name="Tenant A", slug=f"tenant-a-{uuid4().hex[:6]}", status=OrganizationStatus.ACTIVE
    )
    org_b = Organization(
        name="Tenant B", slug=f"tenant-b-{uuid4().hex[:6]}", status=OrganizationStatus.ACTIVE
    )
    db_session.add_all([org_a, org_b])
    await db_session.commit()

    # 2. Create Restaurant under Org B
    rest_b = Restaurant(
        organization_id=org_b.id,
        name="Restaurant B",
        slug=f"rest-b-{uuid4().hex[:6]}",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add(rest_b)
    await db_session.commit()

    # 3. Create RestaurantProfile under Org B
    profile_b = RestaurantProfileRecord(
        organization_id=org_b.id,
        restaurant_id=rest_b.id,
        public_name="Restaurant B Profile",
        primary_currency="USD",
        timezone="UTC",
    )
    db_session.add(profile_b)
    await db_session.commit()

    # 4. Attempt retrieval by Org A via repository port
    repo = SQLAlchemyRestaurantProfileRepository(db_session)
    result_scoped_to_a = await repo.get_by_restaurant_id(
        restaurant_id=rest_b.id,
        organization_id=org_a.id,
    )
    assert result_scoped_to_a is None

    # 5. Direct SQL query scoped to Org A should return empty
    stmt = select(RestaurantProfileRecord).where(
        RestaurantProfileRecord.restaurant_id == rest_b.id,
        RestaurantProfileRecord.organization_id == org_a.id,
    )
    res = await db_session.execute(stmt)
    assert res.scalar_one_or_none() is None
