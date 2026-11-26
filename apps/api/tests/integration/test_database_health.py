"""Integration tests for database health and readiness endpoints (FCD-03 §11.3 & §11.4)."""

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError


def test_database_health_endpoint_healthy(client: TestClient):
    """Verify /api/v1/database/health returns 200 when database query succeeds."""
    with patch(
        "menu_it.api.v1.endpoints.database_health.AsyncSessionFactory"
    ) as mock_session_factory:
        mock_session = mock_session_factory.return_value.__aenter__.return_value
        mock_session.execute.return_value = None

        response = client.get("/api/v1/database/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "reachable"


def test_database_health_endpoint_unreachable(client: TestClient):
    """Verify /api/v1/database/health returns 503 when database query raises SQLAlchemyError."""
    with patch(
        "menu_it.api.v1.endpoints.database_health.AsyncSessionFactory"
    ) as mock_session_factory:
        mock_session = mock_session_factory.return_value.__aenter__.return_value
        mock_session.execute.side_effect = OperationalError("connection refused", {}, None)

        response = client.get("/api/v1/database/health")
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data or "error" in data


def test_readiness_with_database_dependency(app):
    """Verify readiness returns 503 when required database dependency fails."""
    client = TestClient(app)
    app.state.runtime_ready = True
    app.state.require_database = True

    with patch("menu_it.api.v1.endpoints.health.AsyncSessionFactory") as mock_session_factory:
        mock_session = mock_session_factory.return_value.__aenter__.return_value
        mock_session.execute.side_effect = OperationalError("database offline", {}, None)

        response = client.get("/api/v1/health/ready")
        assert response.status_code == 503

    client.close()
