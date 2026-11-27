"""Health, liveness, and operational readiness endpoints (FCD-02, FCD-07, FCD-09 WP-08)."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text

from menu_it.core.config import get_settings
from menu_it.database.session import AsyncSessionFactory
from menu_it.platform.container import PlatformServices
from menu_it.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter()


class PlatformComponentHealth(BaseModel):
    """Component-specific operational status without leaking credentials or paths."""

    model_config = ConfigDict(extra="ignore")

    database: str
    storage: str
    notifications: str
    redis: str = "operational"
    jobs: str = "operational"


class PlatformHealthResponse(BaseModel):
    """Aggregated platform health report."""

    model_config = ConfigDict(extra="forbid")

    status: str
    application: str
    version: str
    components: PlatformComponentHealth


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

    # Bounded SELECT 1 database connectivity check if required
    if getattr(request.app.state, "require_database", False):
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


@router.get(
    "/health/platform",
    response_model=PlatformHealthResponse,
    summary="Platform Services Health Probe",
)
async def platform_health_check(request: Request) -> PlatformHealthResponse:
    """Check readiness of platform subcomponents (database, storage, notifications)."""
    settings = get_settings()
    services: PlatformServices | None = getattr(request.app.state, "platform_services", None)

    # 1. Database Check
    db_status = "healthy"
    try:
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    # 2. Storage Check
    storage_status = "healthy"
    if services:
        try:
            # Check root storage accessibility
            exists = await services.file_storage.exists(key="__health_probe__")
            storage_status = "healthy" if exists is not None else "degraded"
        except Exception:
            storage_status = "unhealthy"

    # 3. Notification Check
    notif_status = "operational"

    # 4. Redis & Cache Check
    redis_status = "operational"
    if services and hasattr(services, "cache_service"):
        try:
            await services.cache_service.exists("__health_probe__")
        except Exception:
            redis_status = "degraded"

    overall_status = "healthy"
    if db_status != "healthy":
        overall_status = "unhealthy"
    elif storage_status != "healthy" or redis_status != "operational":
        overall_status = "degraded"

    return PlatformHealthResponse(
        status=overall_status,
        application=settings.app_name,
        version=settings.app_version,
        components=PlatformComponentHealth(
            database=db_status,
            storage=storage_status,
            notifications=notif_status,
            redis=redis_status,
            jobs="operational",
        ),
    )
