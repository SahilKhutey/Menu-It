import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    # 1. Register a new user
    register_payload = {
        "email": "chef@tajbistro.com",
        "password": "Password123!",
        "full_name": "Chef Sanjeev",
        "organization_name": "Taj Group",
        "restaurant_name": "Taj Bistro Mumbai"
    }
    res = await client.post("/api/v1/auth/register", json=register_payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert "access_token" in data
    assert data["email"] == "chef@tajbistro.com"

    # 2. Login with valid credentials
    login_payload = {
        "email": "chef@tajbistro.com",
        "password": "Password123!"
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 3. Access protected /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "chef@tajbistro.com"


@pytest.mark.asyncio
async def test_invalid_login_rejected(client):
    res = await client.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "wrong"})
    assert res.status_code == 401
