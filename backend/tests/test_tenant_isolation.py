import pytest


@pytest.mark.asyncio
async def test_tenant_isolation_boundary(client):
    # Register Restaurant A
    reg_a = await client.post("/api/v1/auth/register", json={
        "email": "owner_a@resto.com",
        "password": "Password123!",
        "full_name": "Owner A",
        "organization_name": "Org A",
        "restaurant_name": "Cafe Alpha"
    })
    assert reg_a.status_code == 201
    token_a = reg_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register Restaurant B
    reg_b = await client.post("/api/v1/auth/register", json={
        "email": "owner_b@resto.com",
        "password": "Password123!",
        "full_name": "Owner B",
        "organization_name": "Org B",
        "restaurant_name": "Cafe Beta"
    })
    assert reg_b.status_code == 201
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get Restaurant A's ID
    rests_a = await client.get("/api/v1/restaurants", headers=headers_a)
    assert rests_a.status_code == 200
    rest_a_id = rests_a.json()[0]["id"]

    # Get Restaurant B's ID
    rests_b = await client.get("/api/v1/restaurants", headers=headers_b)
    assert rests_b.status_code == 200
    rest_b_id = rests_b.json()[0]["id"]

    # TEST SEC-01: User A attempts to list Restaurant B's menus -> Must be 403 Forbidden
    res_cross_list = await client.get(f"/api/v1/restaurants/{rest_b_id}/menus", headers=headers_a)
    assert res_cross_list.status_code == 403, "User A should not access Restaurant B's menus"

    # TEST SEC-02: User A attempts to create a menu in Restaurant B -> Must be 403 Forbidden
    res_cross_create = await client.post(
        f"/api/v1/restaurants/{rest_b_id}/menus",
        headers=headers_a,
        json={"name": "Hacked Menu", "slug": "hacked-menu"}
    )
    assert res_cross_create.status_code == 403, "User A should not create menus in Restaurant B"

    # TEST SEC-03: User A attempts to modify Restaurant B's design config -> Must be 403 Forbidden
    res_cross_design = await client.put(
        f"/api/v1/restaurants/{rest_b_id}/design",
        headers=headers_a,
        json={"theme_key": "vibrant"}
    )
    assert res_cross_design.status_code == 403, "User A should not alter Restaurant B's design"
