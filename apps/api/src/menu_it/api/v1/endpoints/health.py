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

    if getattr(request.app.state, "require_database", False):
        from sqlalchemy import text

        from menu_it.database.session import AsyncSessionFactory

        try:
            async with AsyncSessionFactory() as session:
                await session.execute(text("SELECT 1"))
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="Database dependency is unreachable.",
            ) from exc

    return ReadinessResponse(
        status="ready",
        ready=True,
    )
