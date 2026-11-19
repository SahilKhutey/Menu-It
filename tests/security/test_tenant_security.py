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


@pytest.mark.asyncio
async def test_arc02_sec_003_menu_editor_denied_platform_admin(client: AsyncClient):
    """
    ARC02-SEC-003:
    A standard restaurant user (non-platform admin) attempting to access
    platform administration endpoints must receive HTTP 403 Forbidden.
    """
    reg = await client.post("/api/v1/auth/register", json={
        "email": "editor_user@resto.com",
        "password": "Password123!",
        "full_name": "Menu Editor",
        "organization_name": "Editor Org",
        "restaurant_name": "Editor Bistro"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to access platform admin route
    resp = await client.get("/api/v1/platform/overview", headers=headers)
    assert resp.status_code == 403
    assert "Platform administration privileges required" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_arc02_sec_004_unpublished_menu_inaccessible_to_public(client: AsyncClient):
    """
    ARC02-SEC-004:
    A public diner attempting to read a restaurant's menu before it has been published
    must receive HTTP 404 Not Found.
    """
    reg = await client.post("/api/v1/auth/register", json={
        "email": "draft_chef@resto.com",
        "password": "Password123!",
        "full_name": "Draft Chef",
        "organization_name": "Draft Group",
        "restaurant_name": "Draft Cafe Only"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    rests = await client.get("/api/v1/restaurants", headers=headers)
    rest_slug = rests.json()[0]["slug"]

    # Public attempts to read menu before publish
    pub_resp = await client.get(f"/api/v1/public/restaurants/{rest_slug}/menu")
    assert pub_resp.status_code == 404


@pytest.mark.asyncio
async def test_arc02_sec_006_malformed_configuration_rejected(client: AsyncClient):
    """
    ARC02-SEC-006:
    Submitting malformed or invalid theme/layout configurations must be rejected with 422.
    """
    reg = await client.post("/api/v1/auth/register", json={
        "email": "cfg_chef@resto.com",
        "password": "Password123!",
        "full_name": "Config Chef",
        "organization_name": "Config Group",
        "restaurant_name": "Config Cafe"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    rests = await client.get("/api/v1/restaurants", headers=headers)
    rest_id = rests.json()[0]["id"]

    # Attempt invalid payload (e.g. non-dictionary tokens)
    resp = await client.put(
        f"/api/v1/restaurants/{rest_id}/design",
        headers=headers,
        json={"theme_key": 12345, "custom_tokens": "not-a-dict"}
    )
    assert resp.status_code == 422


def test_arc02_sec_007_no_committed_secrets():
    """
    ARC02-SEC-007:
    Repository must not contain committed production secret files (.env, private keys).
    """
    from pathlib import Path
    repo_root = Path(__file__).resolve().parent.parent.parent
    forbidden_files = [".env", "id_rsa", "credentials.json", "private_key.pem"]
    for f in forbidden_files:
        p = repo_root / f
        assert not p.exists() or p.is_dir(), f"Security violation (ARC02-SEC-007): Secret file committed: {f}"
