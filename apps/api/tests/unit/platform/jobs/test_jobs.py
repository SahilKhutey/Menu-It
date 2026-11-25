"""Unit tests for background jobs, registry, retry backoff, and DLQ (FCD-10 WP-03, WP-04)."""

from datetime import datetime, timezone
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.background_job import BackgroundJobModel
from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.platform.jobs.contracts import JobContext, JobEnvelope, JobStatus
from menu_it.platform.jobs.dead_letter import DeadLetterService
from menu_it.platform.jobs.registry import (
    JOB_REGISTRY,
    get_job_handler,
    is_valid_job_type,
    register_job_type,
)
from menu_it.platform.jobs.retry import (
    PermanentJobError,
    RetryableJobError,
    calculate_retry_delay,
    is_retryable_error,
)
from menu_it.platform.jobs.service import JobService


async def create_test_org(session: AsyncSession) -> Organization:
    org = Organization(
        name="Test Org",
        slug=f"org-{uuid.uuid4().hex[:8]}",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(org)
    await session.flush()
    return org


def test_job_01_retry_delay_exponential_and_capped():
    # Test exponential doubling
    d1 = calculate_retry_delay(attempt=1, initial_delay=5, maximum_delay=900, multiplier=2, jitter_fraction=0)
    assert d1 == 5.0
    d2 = calculate_retry_delay(attempt=2, initial_delay=5, maximum_delay=900, multiplier=2, jitter_fraction=0)
    assert d2 == 10.0
    d3 = calculate_retry_delay(attempt=3, initial_delay=5, maximum_delay=900, multiplier=2, jitter_fraction=0)
    assert d3 == 20.0

    # Test cap at maximum_delay
    d_capped = calculate_retry_delay(attempt=20, initial_delay=5, maximum_delay=900, multiplier=2, jitter_fraction=0)
    assert d_capped == 900.0


def test_job_02_retry_delay_with_jitter():
    # Mock jitter returning 0.5
    d = calculate_retry_delay(
        attempt=1,
        initial_delay=10,
        maximum_delay=100,
        jitter_fraction=0.2,
        random_fn=lambda: 0.5,
    )
    # base = 10, jitter = 0.5 * 0.2 * 10 = 1.0 -> 11.0
    assert d == 11.0


def test_job_03_failure_classification():
    # Retryable errors
    assert is_retryable_error(ConnectionError("Connection lost")) is True
    assert is_retryable_error(TimeoutError("Read timed out")) is True
    assert is_retryable_error(RetryableJobError("Transient failure")) is True

    # Permanent non-retryable errors
    assert is_retryable_error(ValueError("Invalid payload")) is False
    assert is_retryable_error(TypeError("Wrong argument")) is False
    assert is_retryable_error(KeyError("Missing key")) is False
    assert is_retryable_error(PermanentJobError("Unrecoverable")) is False


def test_job_04_registry_validation():
    register_job_type("test.custom_task", lambda ctx: None)
    assert is_valid_job_type("test.custom_task") is True
    assert is_valid_job_type("nonexistent.task") is False

    with pytest.raises(ValueError, match="Unregistered job type"):
        get_job_handler("nonexistent.task")

    with pytest.raises(ValueError, match="cannot contain ':'"):
        register_job_type("invalid:type", lambda ctx: None)


@pytest.mark.asyncio
async def test_job_05_submit_valid_job(db_session: AsyncSession):
    org = await create_test_org(db_session)
    service = JobService(db_session)
    org_id = org.id
    context = JobContext(
        organization_id=org_id,
        actor_user_id=None,
        correlation_id="corr-123",
        initiated_by="user",
    )
    payload = {"recipient": "user@example.com", "template": "welcome"}

    envelope = await service.submit_job(
        job_type="notification.send",
        payload=payload,
        context=context,
    )
    await db_session.commit()

    assert envelope.job_id is not None
    assert envelope.job_type == "notification.send"
    assert envelope.payload == payload

    # Verify retrieved from DB
    persisted = await service.get_job(envelope.job_id, organization_id=org_id)
    assert persisted is not None
    assert persisted.status == JobStatus.QUEUED.value
    assert persisted.organization_id == org_id


@pytest.mark.asyncio
async def test_job_06_submit_unknown_type_rejected(db_session: AsyncSession):
    service = JobService(db_session)
    context = JobContext(
        organization_id=None,
        actor_user_id=None,
        correlation_id="corr-err",
        initiated_by="system",
    )
    with pytest.raises(ValueError, match="is not registered"):
        await service.submit_job(
            job_type="unregistered.task",
            payload={"data": 1},
            context=context,
        )


@pytest.mark.asyncio
async def test_job_07_idempotency_prevents_duplicate_enqueue(db_session: AsyncSession):
    org = await create_test_org(db_session)
    service = JobService(db_session)
    context = JobContext(
        organization_id=org.id,
        actor_user_id=None,
        correlation_id="corr-idem",
        initiated_by="user",
    )
    idem_key = f"unique-operation-{uuid.uuid4()}"

    env1 = await service.submit_job(
        job_type="file.process",
        payload={"file_id": "file-1"},
        context=context,
        idempotency_key=idem_key,
    )
    await db_session.commit()

    # Second submission with same idempotency key
    env2 = await service.submit_job(
        job_type="file.process",
        payload={"file_id": "file-1"},
        context=context,
        idempotency_key=idem_key,
    )

    # Returns the existing job without creating a new record
    assert env2.job_id == env1.job_id


@pytest.mark.asyncio
async def test_job_08_cancel_queued_job(db_session: AsyncSession):
    org = await create_test_org(db_session)
    service = JobService(db_session)
    org_id = org.id
    context = JobContext(
        organization_id=org_id,
        actor_user_id=None,
        correlation_id="corr-cancel",
        initiated_by="user",
    )
    envelope = await service.submit_job(
        job_type="menu.rebuild",
        payload={"menu_id": "menu-1"},
        context=context,
    )
    await db_session.commit()

    cancelled = await service.cancel_job(envelope.job_id, organization_id=org_id)
    assert cancelled is True
    await db_session.commit()

    job = await service.get_job(envelope.job_id, organization_id=org_id)
    assert job.status == JobStatus.CANCELLED.value


@pytest.mark.asyncio
async def test_job_09_dead_letter_service_lifecycle(db_session: AsyncSession):
    org = await create_test_org(db_session)
    dl_service = DeadLetterService(db_session)
    org_id = org.id
    job_id = uuid.uuid4()
    payload = {"order_id": str(uuid.uuid4())}

    record = await dl_service.record_dead_letter(
        job_id=job_id,
        job_type="notification.send",
        payload=payload,
        failure_code="MAX_ATTEMPTS_EXHAUSTED",
        failure_message="Connection timed out repeatedly.",
        attempts=5,
        correlation_id="corr-dlq",
        organization_id=org_id,
    )
    await db_session.commit()

    assert record.id is not None
    assert record.job_id == job_id
    assert record.replayed_at is None

    # List dead letters
    records = await dl_service.list_dead_letters(organization_id=org_id)
    assert len(records) >= 1
    assert any(r.job_id == job_id for r in records)

    # Mark replayed
    replayed_user = None
    updated = await dl_service.mark_replayed(
        record_id=record.id,
        replayed_by=replayed_user,
        organization_id=org_id,
    )
    await db_session.commit()

    assert updated is not None
    assert updated.replayed_at is not None
