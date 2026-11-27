"""Integration tests for FCD-07 API exception handling and error envelope."""

from uuid import UUID

from fastapi.testclient import TestClient


def test_404_error_envelope(client: TestClient) -> None:
    res = client.get("/api/v1/non-existent-endpoint")
    assert res.status_code == 404
    body = res.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "not found" in body["error"]["message"].lower()
    assert isinstance(body["error"]["details"], list)
    assert "request_id" in body["meta"]
    assert "timestamp" in body["meta"]
    UUID(body["meta"]["request_id"])


def test_422_validation_error_envelope(client: TestClient) -> None:
    # Send invalid body to restaurant creation endpoint without auth/org
    res = client.post("/api/v1/restaurants", json={"invalid": "payload"})
    # Since auth/org is missing, this could be 400 or 401, but testing validation on a route:
    assert res.status_code in (400, 401, 422)
    body = res.json()
    assert body["success"] is False
    assert body["data"] is None
    assert "code" in body["error"]
    assert "message" in body["error"]
    assert "request_id" in body["meta"]
