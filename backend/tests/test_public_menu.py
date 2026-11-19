import pytest


@pytest.mark.asyncio
async def test_end_to_end_publishing_and_public_access(client):
    # 1. Register restaurant
    reg = await client.post("/api/v1/auth/register", json={
        "email": "chef@bombaycanteen.com",
        "password": "Password123!",
        "full_name": "Floyd Cardoz",
        "organization_name": "Hunger Inc",
        "restaurant_name": "The Bombay Canteen"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get restaurant details
    rests = await client.get("/api/v1/restaurants", headers=headers)
    rest_data = rests.json()[0]
    rest_id = rest_data["id"]
    rest_slug = rest_data["slug"]

    # 3. Create a Menu
    menu_res = await client.post(
        f"/api/v1/restaurants/{rest_id}/menus",
        headers=headers,
        json={"name": "Dinner Menu", "slug": "dinner", "menu_type": "dinner"}
    )
    assert menu_res.status_code == 201
    menu_id = menu_res.json()["id"]

    # 4. Create Category
    cat_res = await client.post(
        f"/api/v1/restaurants/{rest_id}/menus/{menu_id}/categories",
        headers=headers,
        json={"name": "Small Plates", "sort_order": 1}
    )
    assert cat_res.status_code == 201
    cat_id = cat_res.json()["id"]

    # 5. Add Food Item with Indian dietary tags & spice level
    item_res = await client.post(
        f"/api/v1/restaurants/{rest_id}/categories/{cat_id}/items",
        headers=headers,
        json={
            "name": "Barley & Jowar Salad",
            "description": "Pomegranate seeds, spiced hung curd, crispy sev",
            "base_price": 425.00,
            "currency_code": "INR",
            "dietary_type": "vegetarian",
            "spice_level": "mild",
            "is_available": True,
            "is_featured": True
        }
    )
    assert item_res.status_code == 201

    # 6. Verify anonymous public access before publishing -> Expect 404 (no published version yet)
    pub_check_before = await client.get(f"/api/v1/public/restaurants/{rest_slug}/menu")
    assert pub_check_before.status_code == 404

    # 7. Publish Menu
    publish_res = await client.post(
        f"/api/v1/restaurants/{rest_id}/menus/{menu_id}/publish",
        headers=headers
    )
    assert publish_res.status_code == 200
    pub_data = publish_res.json()
    assert pub_data["status"] == "published"
    assert pub_data["version_number"] == 1
    assert "checksum" in pub_data

    # 8. Verify anonymous public access after publishing -> Expect 200 with complete snapshot
    pub_check_after = await client.get(f"/api/v1/public/restaurants/{rest_slug}/menu")
    assert pub_check_after.status_code == 200
    snapshot_payload = pub_check_after.json()
    assert snapshot_payload["version_number"] == 1
    assert snapshot_payload["data"]["restaurant"]["name"] == "The Bombay Canteen"
    assert len(snapshot_payload["data"]["categories"]) == 1
    assert snapshot_payload["data"]["categories"][0]["items"][0]["name"] == "Barley & Jowar Salad"
    assert snapshot_payload["data"]["categories"][0]["items"][0]["base_price"] == 425.00
    assert snapshot_payload["data"]["categories"][0]["items"][0]["dietary_type"] == "vegetarian"
