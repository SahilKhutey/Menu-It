"""Integration tests for Internal Jobs and DLQ APIs (FCD-10 WP-09)."""

import uuid
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.api.dependencies.authentication import get_authenticated_principal
from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.database.models.background_job import BackgroundJobModel
from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.models.user import User, UserStatus
from menu_it.database.session import get_db_session
from menu_it.platform.jobs.dead_letter import DeadLetterService


@pytest.fixture
def mock_principal() -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id=uuid.uuid4(),
        is_authenticated=True,
    )


@pytest.mark.asyncio
async def test_internal_jobs_api_submit_and_inspect(
    client: TestClient,
    db_session: AsyncSession,
    mock_principal: AuthenticatedPrincipal,
):
    app = client.app
    app.dependency_overrides[get_authenticated_principal] = lambda: mock_principal
    app.dependency_overrides[get_db_session] = lambda: db_session

    try:
        user = User(
            id=mock_principal.user_id,
            email=f"operator-{uuid.uuid4().hex[:6]}@menu-it.com",
            normalized_email=f"operator-{uuid.uuid4().hex[:6]}@menu-it.com",
            display_name="Operator",
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()

        # 1. Submit job (platform-level job with organization_id=None)
        res_submit = client.post(
            "/api/v1/internal/jobs",
            headers={"X-Request-ID": "test-req-1"},
            json={
                "job_type": "notification.send",
                "payload": {"recipient": "customer@example.com"},
            },
        )
        assert res_submit.status_code == 202
        body = res_submit.json()
        assert body["success"] is True
        job_id = body["data"]["job_id"]
        assert body["data"]["status"] == "queued"

        # 2. Inspect job
        res_get = client.get(f"/api/v1/internal/jobs/{job_id}")
        assert res_get.status_code == 200
        get_body = res_get.json()
        assert get_body["data"]["job_id"] == job_id
        assert get_body["data"]["job_type"] == "notification.send"

        # 3. Cancel job
        res_cancel = client.post(f"/api/v1/internal/jobs/{job_id}/cancel")
        assert res_cancel.status_code == 200
        assert res_cancel.json()["data"]["status"] == "cancelled"

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_internal_dead_letters_api_list_and_replay(
    client: TestClient,
    db_session: AsyncSession,
    mock_principal: AuthenticatedPrincipal,
):
    app = client.app
    app.dependency_overrides[get_authenticated_principal] = lambda: mock_principal
    app.dependency_overrides[get_db_session] = lambda: db_session

    try:
        user = User(
            id=mock_principal.user_id,
            email=f"operator-{uuid.uuid4().hex[:6]}@menu-it.com",
            normalized_email=f"operator-{uuid.uuid4().hex[:6]}@menu-it.com",
            display_name="Operator",
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()

        org = Organization(
            name="DLQ Test Org",
            slug=f"dlq-{uuid.uuid4().hex[:6]}",
            status=OrganizationStatus.ACTIVE,
        )
        db_session.add(org)
        await db_session.flush()

        dl_service = DeadLetterService(db_session)
        rec = await dl_service.record_dead_letter(
            job_id=uuid.uuid4(),
            job_type="notification.send",
            payload={"msg": "alert"},
            failure_code="MAX_RETRIES",
            failure_message="Timeout after 5 tries",
            attempts=5,
            correlation_id="corr-dlq-api",
            organization_id=org.id,
        )
        await db_session.commit()

        # 1. List dead letters
        res_list = client.get(
            "/api/v1/internal/dead-letters",
            headers={"X-Organization-ID": str(org.id)},
        )
        assert res_list.status_code == 200
        list_body = res_list.json()
        assert list_body["success"] is True
        assert len(list_body["data"]) >= 1
        assert any(r["id"] == str(rec.id) for r in list_body["data"])

        # 2. Get specific dead letter
        res_get = client.get(
            f"/api/v1/internal/dead-letters/{rec.id}",
            headers={"X-Organization-ID": str(org.id)},
        )
        assert res_get.status_code == 200
        assert res_get.json()["data"]["failure_code"] == "MAX_RETRIES"

        # 3. Replay dead letter
        res_replay = client.post(
            f"/api/v1/internal/dead-letters/{rec.id}/replay",
            headers={"X-Organization-ID": str(org.id)},
        )
        assert res_replay.status_code == 200
        replay_body = res_replay.json()
        assert replay_body["data"]["status"] == "queued"

    finally:
        app.dependency_overrides.clear()
