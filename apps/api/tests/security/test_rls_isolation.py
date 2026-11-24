"""Security tests for RLS isolation and transaction context binding (FCD-04 §12, §18.5, §18.6)."""

from uuid import uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.organization import (
    Organization,
    OrganizationStatus,
)
from menu_it.database.models.restaurant import (
    Restaurant,
    RestaurantStatus,
)
from menu_it.database.tenant_scope import set_database_tenant_context
from menu_it.database.unit_of_work import TenantUnitOfWork, tenant_transaction
from menu_it.tenancy.context import TenantContext


@pytest.mark.asyncio
async def test_tenant_transaction_context_lifecycle(db_session: AsyncSession):
    """Verify tenant_transaction context manager sets context, commits, and releases cleanly."""
    org = Organization(name="RLS Org", slug="rls-org", status=OrganizationStatus.ACTIVE)
    db_session.add(org)
    await db_session.commit()

    context = TenantContext(
        organization_id=org.id,
        user_id=uuid4(),
        organization_role="owner",
    )

    async with tenant_transaction(db_session, context) as session:
        rest = Restaurant(
            organization_id=org.id,
            name="RLS Bistro",
            slug="rls-bistro",
            status=RestaurantStatus.ACTIVE,
        )
        session.add(rest)

    # Verify committed outside the block
    stmt = select(Restaurant).where(Restaurant.slug == "rls-bistro")
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_tenant_unit_of_work(db_session: AsyncSession):
    """Verify TenantUnitOfWork aenter and aexit behavior."""
    org = Organization(name="UoW Org", slug="uow-org", status=OrganizationStatus.ACTIVE)
    db_session.add(org)
    await db_session.commit()

    context = TenantContext(
        organization_id=org.id,
        user_id=uuid4(),
        organization_role="admin",
    )

    async with TenantUnitOfWork(db_session, context) as uow:
        rest = Restaurant(
            organization_id=org.id,
            name="UoW Bistro",
            slug="uow-bistro",
            status=RestaurantStatus.ACTIVE,
        )
        uow.session.add(rest)

    stmt = select(Restaurant).where(Restaurant.slug == "uow-bistro")
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_set_database_tenant_context_postgres_dialect(db_session: AsyncSession):
    """Verify set_database_tenant_context executes transaction-local setting on PostgreSQL."""
    org_id = uuid4()
    context = TenantContext(
        organization_id=org_id,
        user_id=uuid4(),
        organization_role="owner",
    )

    bind = db_session.bind
    if bind and "postgresql" in bind.dialect.name:
        async with db_session.begin():
            await set_database_tenant_context(db_session, context)
            val = await db_session.execute(
                text("SELECT current_setting('app.current_organization_id', true)")
            )
            assert val.scalar() == str(org_id)
        # Transaction committed: transaction-local setting is cleared
        val_after = await db_session.execute(
            text("SELECT current_setting('app.current_organization_id', true)")
        )
        assert val_after.scalar() in (None, "")
    else:
        # On SQLite / fallback engine, set_database_tenant_context safely no-ops without error
        await set_database_tenant_context(db_session, context)
