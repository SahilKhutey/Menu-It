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
