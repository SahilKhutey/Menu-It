"""Integration tests for operational health endpoints."""

from fastapi.testclient import TestClient


def test_health_endpoint(client):
    """Verify /health returns healthy status and metadata."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["application"] == "Menu-It"
    assert data["version"] == "0.1.0"


def test_liveness_endpoint(client):
    """Verify /health/live returns alive status."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness_after_startup(client):
    """Verify /health/ready returns 200 ready when runtime is initialized."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True


def test_readiness_before_startup(app):
    """Verify /health/ready returns 503 before runtime is initialized."""
    client = TestClient(app)
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    client.close()
