"""Contract tests for OpenAPI schema generation and specification conformance (FCD-07 WP-14)."""

from fastapi.testclient import TestClient


def test_openapi_json_schema(client: TestClient) -> None:
    res = client.get("/api/v1/openapi.json")
    assert res.status_code == 200
    schema = res.json()

    # Verify standard OpenAPI 3.x structure
    assert "openapi" in schema
    assert schema["openapi"].startswith("3.")
    assert "info" in schema
    assert "paths" in schema

    info = schema["info"]
    assert "title" in info
    assert "version" in info

    paths = schema["paths"]
    # Check that core routes are included
    assert "/api/v1/health/live" in paths
    assert "/api/v1/restaurants" in paths
    assert "/api/v1/restaurants/{restaurant_id}" in paths

    # Verify tags
    tags = schema.get("tags", [])
    tag_names = [t["name"] for t in tags]
    assert "Restaurants" in tag_names
    assert "Health" in tag_names
