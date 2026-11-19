"""
Integration tests for Publishing and Snapshot Immutability (ARC-02 §12.1 TC-ARC02-04, TC-ARC02-05, §12.4 TC-ARC02-18, TC-ARC02-19).
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_publishing_creates_immutable_snapshot_and_serves_publicly(client: AsyncClient):
    """
    TC-ARC02-04, TC-ARC02-18, TC-ARC02-19:
    1. Diners require zero authentication to read public menus (P-07, CON-11).
    2. Publishing compiles an immutable snapshot stamped with SHA-256 checksum (P-07).
    3. Subsequent updates create v2 without mutating the historical v1 snapshot.
    """
    # 1. Register restaurant
    reg = await client.post("/api/v1/auth/register", json={
        "email": "chef_tasting@bombaycanteen.com",
        "password": "Password123!",
        "full_name": "Floyd Cardoz",
        "organization_name": "Hunger Inc",
        "restaurant_name": "The Bombay Canteen"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get restaurant ID and slug
    rests = await client.get("/api/v1/restaurants", headers=headers)
    rest_data = rests.json()[0]
    rest_id = rest_data["id"]
    rest_slug = rest_data["slug"]

    # 3. Create a Menu
    menu_res = await client.post(
        f"/api/v1/restaurants/{rest_id}/menus",
        headers=headers,
        json={"name": "Evening Tasting", "slug": "evening-tasting", "menu_type": "dinner"}
    )
    assert menu_res.status_code == 201
    menu_id = menu_res.json()["id"]

    # 4. Create Category
    cat_res = await client.post(
        f"/api/v1/restaurants/{rest_id}/menus/{menu_id}/categories",
        headers=headers,
        json={"name": "Small Bites", "sort_order": 1}
    )
    assert cat_res.status_code == 201
    cat_id = cat_res.json()["id"]

    # 5. Add Dish
    item_res = await client.post(
        f"/api/v1/restaurants/{rest_id}/categories/{cat_id}/items",
        headers=headers,
        json={
            "name": "Barley & Jowar Salad",
            "base_price": "425.00",
            "currency_code": "INR",
            "dietary_type": "vegetarian",
            "spice_level": "mild",
            "is_available": True
        }
    )
    assert item_res.status_code == 201

    # 6. Publish Version 1
    publish_res_v1 = await client.post(
        f"/api/v1/restaurants/{rest_id}/menus/{menu_id}/publish",
        headers=headers
    )
    assert publish_res_v1.status_code == 200
    v1_data = publish_res_v1.json()
    assert v1_data["version_number"] == 1
    assert "checksum" in v1_data
    checksum_v1 = v1_data["checksum"]
    assert len(checksum_v1) == 64  # SHA-256 is 64 hex characters

    # 7. Public guest reads menu (Zero Auth - Principle P-07)
    public_res = await client.get(f"/api/v1/public/restaurants/{rest_slug}/menu")
    assert public_res.status_code == 200
    public_data = public_res.json()
    assert public_data["version_number"] == 1
    assert public_data["checksum"] == checksum_v1
    assert public_data["data"]["restaurant"]["name"] == "The Bombay Canteen"
    assert len(public_data["data"]["categories"]) == 1

    # 8. Add a second dish and publish Version 2
    item2_res = await client.post(
        f"/api/v1/restaurants/{rest_id}/categories/{cat_id}/items",
        headers=headers,
        json={
            "name": "Chettinad Fried Chicken",
            "base_price": "525.00",
            "currency_code": "INR",
            "dietary_type": "non_veg",
            "spice_level": "hot",
            "is_available": True
        }
    )
    assert item2_res.status_code == 201

    publish_res_v2 = await client.post(
        f"/api/v1/restaurants/{rest_id}/menus/{menu_id}/publish",
        headers=headers
    )
    assert publish_res_v2.status_code == 200
    v2_data = publish_res_v2.json()
    assert v2_data["version_number"] == 2
    assert v2_data["checksum"] != checksum_v1

    # 9. Public guest now receives Version 2
    public_res_v2 = await client.get(f"/api/v1/public/restaurants/{rest_slug}/menu")
    assert public_res_v2.status_code == 200
    assert public_res_v2.json()["version_number"] == 2
    assert len(public_res_v2.json()["data"]["categories"][0]["items"]) == 2
