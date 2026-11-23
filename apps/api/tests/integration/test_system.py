"""Integration tests for system information endpoint."""


def test_system_information(client):
    """Verify /system/info returns non-sensitive runtime metadata."""
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "Menu-It"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "development"
    assert data["api_prefix"] == "/api/v1"
