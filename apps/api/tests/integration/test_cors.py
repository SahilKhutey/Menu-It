"""Integration tests for CORS policy enforcement."""


def test_allowed_frontend_origin(client):
    """Verify preflight OPTIONS request from approved origin is permitted."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_unapproved_origin_not_authorized(client):
    """Verify preflight OPTIONS request from unapproved origin is rejected."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "https://unapproved.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in response.headers
