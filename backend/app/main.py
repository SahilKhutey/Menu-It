from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.api.router import api_router
from app.bootstrap import lifespan
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.errors import http_exception_handler, validation_exception_handler
from app.core.middleware import CorrelationIdMiddleware


def create_application() -> FastAPI:
    """Application factory constructing the modular monolith API (ARC-03 §4.3 & §11.1)."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="ModularMenu: Multi-Tenant Configurable Restaurant Menu Platform API",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Register Request Correlation ID Middleware (ARC-03 §6.1)
    application.add_middleware(CorrelationIdMiddleware)

    # Register RFC 7807 Exception Handlers (ARC-02 §4.4 & ARC-03 §6.4)
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)

    # CORS Middleware configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API v1 router
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Consolidated Operational Health Check (ARC-02 §12.5)
    @application.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "deployment_mode": settings.DEPLOYMENT_MODE,
            "environment": settings.ENVIRONMENT
        }

    # Process Liveness Probe (ARC-03 §11.3)
    @application.get("/health/live", tags=["Health"])
    async def liveness_check():
        return {"status": "alive", "service": settings.PROJECT_NAME}

    # Readiness Probe (ARC-03 §11.3 - inspects required dependencies without exposing credentials)
    @application.get("/health/ready", tags=["Health"])
    async def readiness_check():
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            return {
                "status": "ready",
                "service": settings.PROJECT_NAME,
                "database": "connected",
                "redis": "optional_unconfigured"
            }
        except Exception as err:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unready",
                    "service": settings.PROJECT_NAME,
                    "detail": "Database connection verification failed"
                }
            )

    return application


app = create_application()
