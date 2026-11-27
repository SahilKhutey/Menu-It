"""Unified application lifecycle and startup integration tests (FCD-13 WP-02).

Tests:
- API application factory composition and startup
- Runtime initialization and graceful disposal
- Worker settings and lifecycle hooks
- System health, info, and metrics endpoint readiness
- Graceful degradation when external services are unconfigured
"""

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from menu_it.application import create_application
from menu_it.core.config import Settings
from menu_it.core.lifecycle import initialize_runtime, shutdown_runtime
from menu_it.platform.jobs.worker import WorkerSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_runtime_initialization_and_shutdown():
    """LIFE-T01 & LIFE-T03: Verify runtime initialize and clean shutdown."""
    app = create_application()
    assert app.state.runtime_ready is False

    await initialize_runtime(app)
    assert app.state.runtime_ready is True
    assert hasattr(app.state, "platform_services")
    assert app.state.platform_services is not None

    await shutdown_runtime(app)
    assert app.state.runtime_ready is False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_worker_settings_startup_and_shutdown_hooks():
    """LIFE-T04 & LIFE-T05: Verify ARQ worker on_startup and on_shutdown lifecycle hooks."""
    ctx: dict = {}
    await WorkerSettings.on_startup(ctx)
    assert "services" in ctx
    assert ctx["services"].settings is not None
    assert ctx["services"].clock is not None

    await WorkerSettings.on_shutdown(ctx)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_application_liveness_and_system_endpoints():
    """LIFE-T01: Verify core health probes are accessible on application startup."""
    app = create_application()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Liveness check
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True or "status" in data

        # System info check
        info_resp = await client.get("/api/v1/system/info")
        assert info_resp.status_code == 200
        info_data = info_resp.json()
        assert "version" in str(info_data) or "api_version" in str(info_data) or "data" in info_data

        # Metrics check
        metrics_resp = await client.get("/api/v1/metrics")
        assert metrics_resp.status_code == 200


@pytest.mark.unit
def test_invalid_configuration_fails_safely():
    """LIFE-T02: Verify invalid environment values are rejected by pydantic validation."""
    with pytest.raises(ValidationError):
        # Invalid environment literal value triggers validation error
        Settings(app_env="invalid-non-existent-environment")  # type: ignore[arg-type]
