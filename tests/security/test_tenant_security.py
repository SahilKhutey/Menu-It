"""
Security and Tenant Isolation Test Suite (ARC-02 §10 WP-ARC02-06, §12.2 TC-ARC02-06 to TC-ARC02-10).
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(client: AsyncClient):
    """
    TC-ARC02-06 / SEC-001:
    Accessing protected management routes without an Authorization header
    must be immediately rejected with HTTP 401 Unauthorized.
    """
    endpoints = [
        "/api/v1/restaurants",
        "/api/v1/restaurants/00000000-0000-0000-0000-000000000000/menus",
        "/api/v1/restaurants/00000000-0000-0000-0000-000000000000/design",
    ]
    for ep in endpoints:
        resp = await client.get(ep)
        assert resp.status_code == 401, f"Expected 401 for unauthenticated request to {ep}"


@pytest.mark.asyncio
async def test_cross_tenant_isolation_strictly_enforced(client: AsyncClient):
    """
    TC-ARC02-07 / SEC-002:
    A user authenticated with Tenant A must be strictly denied access (HTTP 403)
    to all resources belonging to Tenant B.
    """
    # 1. Register Tenant A
    reg_a = await client.post("/api/v1/auth/register", json={
        "email": "owner_alpha@test.com",
        "password": "Password123!",
        "full_name": "Alpha Owner",
        "organization_name": "Alpha Corp",
        "restaurant_name": "Alpha Bistro"
    })
    assert reg_a.status_code == 201
    token_a = reg_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register Tenant B
    reg_b = await client.post("/api/v1/auth/register", json={
        "email": "owner_beta@test.com",
        "password": "Password123!",
        "full_name": "Beta Owner",
        "organization_name": "Beta Corp",
        "restaurant_name": "Beta Dining"
    })
    assert reg_b.status_code == 201
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Retrieve Tenant B restaurant ID
    rests_b = await client.get("/api/v1/restaurants", headers=headers_b)
    assert rests_b.status_code == 200
    rest_b_id = rests_b.json()[0]["id"]

    # 4. Attempt cross-tenant menu read
    resp_cross_get = await client.get(f"/api/v1/restaurants/{rest_b_id}/menus", headers=headers_a)
    assert resp_cross_get.status_code == 403

    # 5. Attempt cross-tenant menu creation
    resp_cross_post = await client.post(
        f"/api/v1/restaurants/{rest_b_id}/menus",
        headers=headers_a,
        json={"name": "Hacked Menu", "slug": "hacked-menu"}
    )
    assert resp_cross_post.status_code == 403

    # 6. Attempt cross-tenant theme modification
    resp_cross_theme = await client.put(
        f"/api/v1/restaurants/{rest_b_id}/design",
        headers=headers_a,
        json={"theme_key": "vibrant"}
    )
    assert resp_cross_theme.status_code == 403


@pytest.mark.asyncio
async def test_tampered_token_rejected(client: AsyncClient):
    """
    TC-ARC02-10:
    A forged or tampered JWT token must be rejected with HTTP 401 Unauthorized.
    """
    tampered_headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.tampered_signature"}
    resp = await client.get("/api/v1/restaurants", headers=tampered_headers)
    assert resp.status_code == 401
