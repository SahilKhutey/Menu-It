"""Integration tests for request ID correlation middleware."""

from uuid import UUID


def test_request_id_is_generated(client):
    """Verify request ID is generated and attached to response headers."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    request_id = response.headers.get("X-Request-ID")
    assert request_id is not None
    # Must be valid UUID
    UUID(request_id)


def test_valid_request_id_is_preserved(client):
    """Verify valid client-provided request ID is preserved."""
    request_id = "f7c8a3e1-9c6a-4a8c-bfe1-2f15c9d1a311"
    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": request_id},
    )
    assert response.headers["X-Request-ID"] == request_id


def test_invalid_request_id_is_replaced(client):
    """Verify invalid client request ID is replaced with a generated UUID."""
    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": "invalid-non-uuid-string"},
    )
    generated_id = response.headers["X-Request-ID"]
    assert generated_id != "invalid-non-uuid-string"
    UUID(generated_id)
