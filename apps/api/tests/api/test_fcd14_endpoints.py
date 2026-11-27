"""End-to-end API endpoint tests for FCD-14 Organization, Restaurant, and Branch workflows."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.tokens import create_access_token
from menu_it.core.config import get_settings
from menu_it.database.models.user import User, UserStatus
from menu_it.sessions.service import SessionService


@pytest.mark.asyncio
async def test_fcd14_full_api_hierarchy_workflow(
    authed_client: TestClient,
    db_session: AsyncSession,
) -> None:
    settings = get_settings()

    # 1. Create authenticated user & session
    user = User(
        email=f"founder-{uuid4().hex[:6]}@menu-it.com",
        normalized_email=f"founder-{uuid4().hex[:6]}@menu-it.com",
        display_name="Founder",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    session_svc = SessionService(db_session)
    user_session, _ = await session_svc.create_session(user_id=user.id, ip_address="127.0.0.1")
    token = create_access_token(
        user_id=user.id,
        session_id=user_session.id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=600,
    )
    await db_session.commit()

    auth_headers = {"Authorization": f"Bearer {token}"}

    # 2. Onboard Organization via POST /api/v1/organizations
    org_resp = authed_client.post(
        "/api/v1/organizations",
        json={
            "name": "ABC Hospitality",
            "slug": f"abc-{uuid4().hex[:6]}",
            "currency_code": "INR",
            "timezone": "Asia/Kolkata",
            "country_code": "IN",
        },
        headers=auth_headers,
    )
    assert org_resp.status_code == 201
    org_data = org_resp.json()["data"]
    org_id = org_data["id"]
    assert org_data["status"] == "active"

    # 3. List Organizations
    list_resp = authed_client.get("/api/v1/organizations", headers=auth_headers)
    assert list_resp.status_code == 200
    assert any(o["id"] == org_id for o in list_resp.json()["data"])

    # 4. Create Restaurant under Organization
    rest_resp = authed_client.post(
        f"/api/v1/organizations/{org_id}/restaurants",
        json={"name": "Spice Garden", "slug": "spice-garden", "timezone": "Asia/Kolkata"},
        headers=auth_headers,
    )
    assert rest_resp.status_code == 201
    rest_id = rest_resp.json()["data"]["id"]

    # 5. Create Branch under Restaurant
    tenant_headers = {**auth_headers, "X-Organization-ID": org_id}
    branch_resp = authed_client.post(
        f"/api/v1/restaurants/{rest_id}/branches",
        json={
            "name": "Spice Garden — Raipur",
            "slug": "raipur",
            "city": "Raipur",
            "country_code": "IN",
            "timezone": "Asia/Kolkata",
        },
        headers=tenant_headers,
    )
    assert branch_resp.status_code == 201
    branch_id = branch_resp.json()["data"]["id"]

    # 6. Get & Update Branch
    patch_resp = authed_client.patch(
        f"/api/v1/branches/{branch_id}",
        json={"city": "Raipur CG", "branch_code": "SG-RPR-01"},
        headers=tenant_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["branch_code"] == "SG-RPR-01"
