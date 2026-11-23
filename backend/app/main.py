from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.router import api_router
from app.bootstrap import lifespan
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.errors import register_error_handlers
from app.core.middleware import CorrelationIdMiddleware


def create_application() -> FastAPI:
    """Application factory constructing the modular monolith API (ARC-03 §4.3 & §11.1)."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="ModularMenu: Multi-Tenant Configurable Restaurant Menu Platform API",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register Request Correlation ID Middleware (ARC-03 §6.1)
    application.add_middleware(CorrelationIdMiddleware)

    # Register Central RFC 7807 / RFC 9457 Exception Handlers (ARC-02 §4.4, ARC-03 §6.4, ARC-07 §5.5, §14.6)
    register_error_handlers(application)

    # CORS Middleware configuration (ARC-07 §14.5, §20.2 ARC07-T069, ARC07-T075)
    cors_origins = [settings.PUBLIC_BASE_URL]
    if settings.ENVIRONMENT in ("development", "test"):
        cors_origins.extend(["http://localhost:3000", "http://127.0.0.1:3000", "http://test"])

    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API v1 router
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Consolidated Operational Health Check (ARC-02 §12.5, ARC-11 §16.2)
    @application.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "deployment_mode": settings.DEPLOYMENT_MODE,
            "environment": settings.APP_ENV,
        }

    # Process Liveness Probe (ARC-03 §11.3, ARC-11 §16.2)
    @application.get("/health/live", tags=["Health"])
    async def liveness_check():
        return {"status": "alive", "service": settings.APP_NAME}

    # Readiness Probe (ARC-03 §11.3, ARC-11 §16.2 - inspects dependencies without exposing credentials)
    @application.get("/health/ready", tags=["Health"])
    async def readiness_check():
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            redis_status = "disabled"
            if settings.REDIS_ENABLED:
                redis_status = "connected" if settings.REDIS_URL else "unconfigured"
            return {
                "status": "ready",
                "service": settings.APP_NAME,
                "database": "connected",
                "redis": redis_status,
            }
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not_ready",
                    "service": settings.APP_NAME,
                    "database": "unavailable",
                    "redis": "skipped",
                },
            )

    # Startup Initialization Probe (ARC-11 §16.2)
    @application.get("/health/startup", tags=["Health"])
    async def startup_check():
        return {
            "status": "started",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    return application


app = create_application()
