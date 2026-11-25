"""Unit tests for platform service container and health probes (FCD-09 WP-07, WP-08)."""

from fastapi.testclient import TestClient
import pytest

from menu_it.application import create_application
from menu_it.core.config import Settings
from menu_it.platform.container import build_platform_services


def test_build_platform_services_initializes_adapters():
    """PlatformServices composition root constructs all adapters cleanly."""
    cfg = Settings(app_env="test")
    container = build_platform_services(cfg)

    assert container.settings.app_name == "Menu-It"
    assert container.clock is not None
    assert container.file_storage is not None
    assert container.notification_service is not None
    assert container.audit_publisher is not None


@pytest.mark.asyncio
async def test_platform_health_endpoints():
    """FastAPI application exposes /health, /health/live, /health/ready, and /health/platform."""
    app = create_application()
    with TestClient(app) as client:
        # Liveness
        res_live = client.get("/api/v1/health/live")
        assert res_live.status_code == 200
        assert res_live.json() == {"status": "alive"}

        # Basic Health
        res_health = client.get("/api/v1/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"

        # Platform Component Health
        res_platform = client.get("/api/v1/health/platform")
        assert res_platform.status_code == 200
        data = res_platform.json()
        assert "components" in data
        assert "storage" in data["components"]
        assert "notifications" in data["components"]
