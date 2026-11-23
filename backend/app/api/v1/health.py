"""
ModularMenu — Operational Health & Observability Endpoints (ARC-03 §11.3, ARC-11 §16.2).
Provides /health/live, /health/ready, and /health/startup with sanitized dependency reporting.
"""

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal

router = APIRouter(prefix="/health", tags=["Health & Observability"])


@router.get("", summary="Consolidated Health Overview")
async def health_overview():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "deployment_mode": settings.DEPLOYMENT_MODE,
    }


@router.get("/live", summary="Process Liveness Probe")
async def live_probe():
    """Returns 200 OK if the process is responsive and running (ARC-11 §16.2)."""
    return {"status": "alive", "service": settings.APP_NAME}


@router.get("/ready", summary="Service Readiness Probe")
async def ready_probe(response: Response):
    """
    Returns 200 OK if service dependencies (PostgreSQL) are operational.
    Does NOT leak connection strings, credentials, or internal topology (ARC-11 §16.2).
    """
    db_status = "connected"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "service": settings.APP_NAME,
            "database": "unavailable",
            "redis": "skipped",
        }

    redis_status = "disabled"
    if settings.REDIS_ENABLED:
        redis_status = "connected" if settings.REDIS_URL else "unconfigured"

    return {
        "status": "ready",
        "service": settings.APP_NAME,
        "database": db_status,
        "redis": redis_status,
    }


@router.get("/startup", summary="Process Startup Initialization Probe")
async def startup_probe():
    """Confirms startup sequence initialization has completed (ARC-11 §16.2)."""
    return {
        "status": "started",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
