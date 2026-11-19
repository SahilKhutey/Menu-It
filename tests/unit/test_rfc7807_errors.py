"""
Unit tests for RFC 7807 Problem Details Error Representation (ARC-02 §4.4, §12.3 TC-ARC02-13, CON-08).
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_not_found_returns_rfc7807_format(client: AsyncClient):
    """
    TC-ARC02-13 / CON-08:
    A 404 Not Found error must return Content-Type: application/problem+json
    with type, title, status, detail, and instance fields.
    """
    response = await client.get("/api/v1/public/restaurants/non-existent-restaurant-slug-999/menu")
    assert response.status_code == 404
    assert response.headers.get("content-type") == "application/problem+json"

    data = response.json()
    assert data["status"] == 404
    assert data["title"] == "Not Found"
    assert "type" in data
    assert "detail" in data
    assert "instance" in data
    assert data["instance"] == "/api/v1/public/restaurants/non-existent-restaurant-slug-999/menu"


@pytest.mark.asyncio
async def test_unauthorized_returns_rfc7807_format(client: AsyncClient):
    """
    TC-ARC02-06 / CON-08:
    Unauthenticated access to protected endpoint returns RFC 7807 problem details.
    """
    response = await client.get("/api/v1/restaurants/00000000-0000-0000-0000-000000000000/menus")
    assert response.status_code == 401
    assert response.headers.get("content-type") == "application/problem+json"

    data = response.json()
    assert data["status"] == 401
    assert data["title"] == "Unauthorized"
    assert "detail" in data
    assert "instance" in data


@pytest.mark.asyncio
async def test_arc02_api_002_invalid_pagination_returns_rfc7807_validation_error(client: AsyncClient):
    """
    ARC02-API-002:
    Passing invalid pagination parameters (e.g. limit=0, offset=-1) must trigger
    a 422 Unprocessable Entity error formatted as RFC 7807 problem details.
    """
    # 1. Register a user to obtain auth token
    reg = await client.post("/api/v1/auth/register", json={
        "email": "page_tester@resto.com",
        "password": "Password123!",
        "full_name": "Pagination Tester",
        "organization_name": "Page Org",
        "restaurant_name": "Page Cafe"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Query with limit=0 (fails ge=1 constraint)
    resp = await client.get("/api/v1/restaurants?limit=0", headers=headers)
    assert resp.status_code == 422
    assert resp.headers.get("content-type") == "application/problem+json"

    data = resp.json()
    assert data["status"] == 422
    assert data["title"] == "Validation Error"
    assert "invalid_params" in data
    assert any("limit" in str(err) for err in data["invalid_params"])

    # Query with offset=-5 (fails ge=0 constraint)
    resp2 = await client.get("/api/v1/restaurants?offset=-5", headers=headers)
    assert resp2.status_code == 422
    data2 = resp2.json()
    assert any("offset" in str(err) for err in data2["invalid_params"])
