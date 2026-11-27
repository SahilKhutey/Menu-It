"""API endpoint tests for FCD-15 Restaurant Profile, Branding, Hours, Services & Publishing."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.tokens import create_access_token
from menu_it.core.config import get_settings
from menu_it.database.models.user import User, UserStatus
from menu_it.sessions.service import SessionService


@pytest.mark.asyncio
async def test_fcd15_full_configuration_and_publication_api(
    authed_client: TestClient,
    db_session: AsyncSession,
) -> None:
    settings = get_settings()
    user = User(
        email=f"cfg-{uuid4().hex[:6]}@menu-it.com",
        normalized_email=f"cfg-{uuid4().hex[:6]}@menu-it.com",
        display_name="Config Owner",
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
    headers = {"Authorization": f"Bearer {token}"}

    org_resp = authed_client.post(
        "/api/v1/organizations",
        json={"name": "Config Group", "slug": f"cfg-{uuid4().hex[:6]}"},
        headers=headers,
    )
    assert org_resp.status_code == 201
    org_id = org_resp.json()["data"]["id"]
    tenant_headers = {**headers, "X-Organization-ID": org_id}

    rest_resp = authed_client.post(
        f"/api/v1/organizations/{org_id}/restaurants",
        json={"name": "Tandoor House", "slug": f"tandoor-{uuid4().hex[:6]}"},
        headers=tenant_headers,
    )
    assert rest_resp.status_code == 201
    rest_id = rest_resp.json()["data"]["id"]

    # Update profile
    prof_resp = authed_client.patch(
        f"/api/v1/restaurants/{rest_id}/profile",
        json={"display_name": "Tandoor House Official", "cuisine_type": "North Indian"},
        headers=tenant_headers,
    )
    assert prof_resp.status_code == 200
    assert prof_resp.json()["data"]["display_name"] == "Tandoor House Official"

    # Update branding
    brand_resp = authed_client.put(
        f"/api/v1/restaurants/{rest_id}/branding",
        json={"primary_color": "#D97706", "font_family": "Playfair Display"},
        headers=tenant_headers,
    )
    assert brand_resp.status_code == 200
    assert brand_resp.json()["data"]["primary_color"] == "#D97706"

    # Update weekly hours & services
    hours_resp = authed_client.put(
        f"/api/v1/restaurants/{rest_id}/hours",
        json={
            "days": [
                {
                    "day_of_week": 0,
                    "is_closed": False,
                    "intervals": [{"opens_at": "11:00:00", "closes_at": "23:00:00"}],
                }
            ]
        },
        headers=tenant_headers,
    )
    assert hours_resp.status_code == 200

    svc_resp = authed_client.put(
        f"/api/v1/restaurants/{rest_id}/services",
        json={"modes": [{"service_type": "DINE_IN", "enabled": True}]},
        headers=tenant_headers,
    )
    assert svc_resp.status_code == 200

    # Publish and fetch public profile without auth
    pub_slug = f"tandoor-pub-{uuid4().hex[:6]}"
    pub_resp = authed_client.post(
        f"/api/v1/restaurants/{rest_id}/publish",
        json={"public_slug": pub_slug},
        headers=tenant_headers,
    )
    assert pub_resp.status_code == 200
    assert pub_resp.json()["data"]["status"] == "published"

    public_resp = authed_client.get(f"/api/v1/public/restaurants/{pub_slug}")
    assert public_resp.status_code == 200
    assert public_resp.json()["data"]["display_name"] == "Tandoor House Official"

    # Unpublish revokes public lookup
    unpub_resp = authed_client.post(
        f"/api/v1/restaurants/{rest_id}/unpublish",
        headers=tenant_headers,
    )
    assert unpub_resp.status_code == 200
    assert authed_client.get(f"/api/v1/public/restaurants/{pub_slug}").status_code == 404
