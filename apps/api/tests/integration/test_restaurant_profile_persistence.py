"""Integration tests for RestaurantProfileRecord database persistence (FCD-06 §14)."""

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.database.models.restaurant_profile import RestaurantProfileRecord


@pytest.mark.asyncio
async def test_restaurant_profile_cascade_delete(db_session: AsyncSession) -> None:
    org = Organization(
        name="Cascade Org", slug=f"cascade-org-{uuid4().hex[:6]}", status=OrganizationStatus.ACTIVE
    )
    db_session.add(org)
    await db_session.commit()

    rest = Restaurant(
        organization_id=org.id,
        name="Cascade Rest",
        slug=f"cascade-rest-{uuid4().hex[:6]}",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add(rest)
    await db_session.commit()

    profile_rec = RestaurantProfileRecord(
        organization_id=org.id,
        restaurant_id=rest.id,
        public_name="Cascade Profile",
        primary_currency="USD",
        timezone="UTC",
    )
    db_session.add(profile_rec)
    await db_session.commit()

    # Verify profile exists
    stmt = select(RestaurantProfileRecord).where(RestaurantProfileRecord.id == profile_rec.id)
    res = await db_session.execute(stmt)
    assert res.scalar_one_or_none() is not None

    # Delete restaurant
    await db_session.delete(rest)
    await db_session.commit()

    # Profile should be cascade deleted
    res_after = await db_session.execute(stmt)
    assert res_after.scalar_one_or_none() is None
