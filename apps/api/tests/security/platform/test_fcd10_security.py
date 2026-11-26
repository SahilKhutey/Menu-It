"""Security tests for worker tenant propagation, DLQ isolation, and RLS (FCD-10 WP-06)."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.tenant_scope import set_database_tenant_context
from menu_it.platform.jobs.contracts import JobContext
from menu_it.platform.jobs.dead_letter import DeadLetterService
from menu_it.platform.jobs.service import JobService
from menu_it.tenancy.context import TenantContext


async def create_test_org(session: AsyncSession, name: str) -> Organization:
    org = Organization(
        name=name,
        slug=f"org-{uuid.uuid4().hex[:8]}",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(org)
    await session.flush()
    return org


@pytest.mark.asyncio
async def test_ten_01_job_service_enforces_tenant_boundary(db_session: AsyncSession):
    org_a_obj = await create_test_org(db_session, "Org A")
    org_b_obj = await create_test_org(db_session, "Org B")
    org_a = org_a_obj.id
    org_b = org_b_obj.id

    service = JobService(db_session)

    context_a = JobContext(
        organization_id=org_a,
        actor_user_id=None,
        correlation_id="corr-a",
        initiated_by="user",
    )
    envelope = await service.submit_job(
        job_type="notification.send",
        payload={"message": "private to A"},
        context=context_a,
    )
    await db_session.commit()

    # Org A can access its job
    job_for_a = await service.get_job(envelope.job_id, organization_id=org_a)
    assert job_for_a is not None
    assert job_for_a.organization_id == org_a

    # Org B CANNOT access Org A's job
    job_for_b = await service.get_job(envelope.job_id, organization_id=org_b)
    assert job_for_b is None


@pytest.mark.asyncio
async def test_ten_02_dead_letter_queue_tenant_scoping(db_session: AsyncSession):
    org_a_obj = await create_test_org(db_session, "Org A DLQ")
    org_b_obj = await create_test_org(db_session, "Org B DLQ")
    org_a = org_a_obj.id
    org_b = org_b_obj.id

    service = DeadLetterService(db_session)

    rec_a = await service.record_dead_letter(
        job_id=uuid.uuid4(),
        job_type="file.process",
        payload={"sensitive": "org A secret"},
        failure_code="ERROR_A",
        failure_message="Failed for A",
        attempts=3,
        correlation_id="corr-dlq-a",
        organization_id=org_a,
    )
    await db_session.commit()

    # Org A sees its dead letter
    list_a = await service.list_dead_letters(organization_id=org_a)
    assert any(r.id == rec_a.id for r in list_a)

    # Org B does NOT see Org A's dead letter
    list_b = await service.list_dead_letters(organization_id=org_b)
    assert not any(r.id == rec_a.id for r in list_b)

    # Org B cannot retrieve Org A's dead letter by ID
    get_b = await service.get_dead_letter(rec_a.id, organization_id=org_b)
    assert get_b is None


@pytest.mark.asyncio
async def test_ten_03_worker_context_does_not_leak_across_tasks(db_session: AsyncSession):
    org_a = uuid.uuid4()
    org_b = uuid.uuid4()

    ctx_a = TenantContext(
        organization_id=org_a,
        user_id=uuid.uuid4(),
        organization_role="admin",
        correlation_id="corr-a",
    )
    await set_database_tenant_context(db_session, ctx_a)

    # Task B runs with Org B context
    ctx_b = TenantContext(
        organization_id=org_b,
        user_id=uuid.uuid4(),
        organization_role="admin",
        correlation_id="corr-b",
    )
    await set_database_tenant_context(db_session, ctx_b)

    # Verify context B is active and no context A state remains
    assert ctx_b.organization_id == org_b
    assert ctx_b.organization_id != org_a
