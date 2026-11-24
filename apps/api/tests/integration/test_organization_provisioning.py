"""Integration tests for OrganizationProvisioningService (FCD-04 §16)."""

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.organization import (
    Organization,
    OrganizationStatus,
)
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationRole,
)
from menu_it.database.models.restaurant import (
    Restaurant,
    RestaurantStatus,
)
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.services.organization_provisioning import OrganizationProvisioningService


@pytest.mark.asyncio
async def test_atomic_provisioning_success(db_session: AsyncSession):
    """Verify atomic provisioning creates organization, membership, and restaurant."""
    service = OrganizationProvisioningService(db_session)
    owner_id = uuid4()

    org, owner_mem, initial_rest = await service.provision_organization(
        name="Trattoria Bella",
        slug="trattoria-bella",
        owner_user_id=owner_id,
        initial_restaurant_name="Bella Downtown",
        initial_restaurant_slug="downtown",
        correlation_id="prov-100",
    )

    assert org.id is not None
    assert org.status == OrganizationStatus.ACTIVE
    assert owner_mem.organization_id == org.id
    assert owner_mem.user_id == owner_id
    assert owner_mem.role == OrganizationRole.OWNER
    assert owner_mem.status == MembershipStatus.ACTIVE

    assert initial_rest is not None
    assert initial_rest.organization_id == org.id
    assert initial_rest.slug == "downtown"
    assert initial_rest.status == RestaurantStatus.ACTIVE

    # Verify audit event is recorded
    audit_stmt = select(OrganizationAuditEvent).where(
        OrganizationAuditEvent.organization_id == org.id
    )
    audit_result = await db_session.execute(audit_stmt)
    event = audit_result.scalar_one_or_none()
    assert event is not None
    assert event.action == "organization.provisioned"
    assert event.actor_id == owner_id
    assert event.correlation_id == "prov-100"


@pytest.mark.asyncio
async def test_duplicate_slug_provisioning_rollback(db_session: AsyncSession):
    """Verify duplicate slug rejection rolls back completely leaving zero orphaned records."""
    service = OrganizationProvisioningService(db_session)
    owner_1 = uuid4()

    # 1. Provision baseline organization
    await service.provision_organization(
        name="Existing Org",
        slug="duplicate-slug-org",
        owner_user_id=owner_1,
    )

    # 2. Attempt duplicate provisioning
    owner_2 = uuid4()
    with pytest.raises(ResourceConflictError) as exc_info:
        await service.provision_organization(
            name="Conflicting Org Attempt",
            slug="duplicate-slug-org",
            owner_user_id=owner_2,
            initial_restaurant_name="Should Not Exist",
            initial_restaurant_slug="should-not-exist",
        )

    assert "already taken" in str(exc_info.value) or "conflict" in str(exc_info.value)

    # 3. Verify no extra organization or orphaned restaurant was created
    orgs_stmt = select(Organization).where(Organization.slug == "duplicate-slug-org")
    all_orgs = list((await db_session.execute(orgs_stmt)).scalars().all())
    assert len(all_orgs) == 1

    rest_stmt = select(Restaurant).where(Restaurant.slug == "should-not-exist")
    orphaned_rests = list((await db_session.execute(rest_stmt)).scalars().all())
    assert len(orphaned_rests) == 0
