"""Security tests for Tenant API endpoints and authorization boundaries (FCD-04 §10, §18.8)."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.organization import (
    Organization,
    OrganizationStatus,
)
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationMembership,
    OrganizationRole,
)
from menu_it.database.session import get_db_session


@pytest.fixture
def authed_client(app, db_session: AsyncSession):
    """Provide a TestClient with get_db_session wired to the active test database session."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = _override_get_db
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_endpoint_requires_authentication(client: TestClient):
    """Verify endpoint rejects requests missing authentication credentials with HTTP 401."""
    random_org = uuid4()
    response = client.get(f"/api/v1/organizations/{random_org}/current")
    assert response.status_code == 401
    assert "Authentication credentials are required" in response.text


@pytest.mark.asyncio
async def test_endpoint_rejects_malformed_user_id(client: TestClient):
    """Verify endpoint rejects invalid user UUID format with HTTP 401."""
    random_org = uuid4()
    response = client.get(
        f"/api/v1/organizations/{random_org}/current",
        headers={"X-User-ID": "invalid-uuid-string"},
    )
    assert response.status_code == 401
    assert "Invalid user identification format" in response.text


@pytest.mark.asyncio
async def test_endpoint_unrelated_user_returns_404(
    authed_client: TestClient, db_session: AsyncSession
):
    """Verify user without membership in the organization receives HTTP 404."""
    org = Organization(
        name="Private Org",
        slug="private-org",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org)
    await db_session.commit()

    unrelated_user = uuid4()
    response = authed_client.get(
        f"/api/v1/organizations/{org.id}/current",
        headers={"X-User-ID": str(unrelated_user)},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_endpoint_suspended_org_returns_403(
    authed_client: TestClient, db_session: AsyncSession
):
    """Verify member of suspended organization is denied access with HTTP 403."""
    user_id = uuid4()
    org = Organization(
        name="Suspended Org API",
        slug="suspended-org-api",
        status=OrganizationStatus.SUSPENDED,
    )
    db_session.add(org)
    await db_session.commit()

    mem = OrganizationMembership(
        organization_id=org.id,
        user_id=user_id,
        role=OrganizationRole.OWNER,
        status=MembershipStatus.ACTIVE,
    )
    db_session.add(mem)
    await db_session.commit()

    response = authed_client.get(
        f"/api/v1/organizations/{org.id}/current",
        headers={"X-User-ID": str(user_id)},
    )
    assert response.status_code == 403
    assert "suspended" in response.text.lower()


@pytest.mark.asyncio
async def test_endpoint_authorized_member_returns_context(
    authed_client: TestClient, db_session: AsyncSession
):
    """Verify authorized member retrieves resolved TenantContext enveloped response."""
    user_id = uuid4()
    org = Organization(
        name="Success Org",
        slug="success-org",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org)
    await db_session.commit()

    mem = OrganizationMembership(
        organization_id=org.id,
        user_id=user_id,
        role=OrganizationRole.ADMIN,
        status=MembershipStatus.ACTIVE,
    )
    db_session.add(mem)
    await db_session.commit()

    correlation_id = str(uuid4())
    response = authed_client.get(
        f"/api/v1/organizations/{org.id}/current",
        headers={
            "X-User-ID": str(user_id),
            "X-Request-ID": correlation_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["organization_id"] == str(org.id)
    assert data["data"]["user_id"] == str(user_id)
    assert data["data"]["organization_role"] == "admin"
    assert data["meta"]["request_id"] == correlation_id
