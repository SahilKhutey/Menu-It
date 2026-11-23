"""Health and readiness endpoints."""

from fastapi import APIRouter, HTTPException, Request

from menu_it.core.config import get_settings
from menu_it.schemas.health import (
    HealthResponse,
    ReadinessResponse,
)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health Check",
)
async def health_check() -> HealthResponse:
    """Return basic application health."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        application=settings.app_name,
        version=settings.app_version,
    )


@router.get(
    "/health/live",
    summary="Application Liveness Probe",
)
async def liveness_check() -> dict[str, str]:
    """Indicate that the process is responsive."""
    return {"status": "alive"}


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Application Readiness Probe",
)
async def readiness_check(request: Request) -> ReadinessResponse:
    """Indicate whether the application runtime is ready to accept requests."""
    is_ready = getattr(request.app.state, "runtime_ready", False)
    if not is_ready:
        raise HTTPException(
            status_code=503,
            detail="Application runtime is not ready.",
        )
    return ReadinessResponse(
        status="ready",
        ready=True,
    )
