"""
Operational and Deployment Health Tests (ARC-02 §12.5 TC-ARC02-20 to TC-ARC02-22).
"""
import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_health_check_returns_operational_status(client: AsyncClient):
    """
    TC-ARC02-20 / DEP-004:
    The /health probe must return HTTP 200 with service metadata,
    deployment mode, and environment for container orchestration probes.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ModularMenu"
    assert "version" in data
    assert "deployment_mode" in data
    assert "environment" in data


def test_dual_profile_configuration_settings():
    """
    TC-ARC02-22 / P-08 / CON-10:
    The application configuration dynamically recognizes both Managed SaaS
    and Customer-Hosted profiles without altering application code.
    """
    assert settings.DEPLOYMENT_MODE in ["managed", "customer_hosted"]
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.ALGORITHM == "HS256"
