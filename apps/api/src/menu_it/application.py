"""Application factory for the Menu-It API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from menu_it.api.exceptions.handlers import register_api_exception_handlers
from menu_it.api.middleware.request_id import RequestIDMiddleware
from menu_it.api.middleware.request_logging import RequestLoggingMiddleware
from menu_it.api.middleware.security_headers import SecurityHeadersMiddleware
from menu_it.api.middleware.timing import RequestTimingMiddleware
from menu_it.api.v1.router import api_router
from menu_it.core.config import get_settings
from menu_it.core.lifecycle import initialize_runtime, shutdown_runtime
from menu_it.core.logging import configure_logging
from menu_it.core.metadata import API_VERSION, APP_DESCRIPTION, APP_TITLE
from menu_it.exceptions.handlers import register_exception_handlers

OPENAPI_TAGS = [
    {
        "name": "Health",
        "description": "System health, liveness, and readiness probes.",
    },
    {
        "name": "Restaurants",
        "description": "Multi-tenant restaurant location management and discovery.",
    },
    {
        "name": "Profiles",
        "description": "Restaurant public profile, schedules, and branding management.",
    },
]


def create_application() -> FastAPI:
    """Create and configure a Menu-It application."""
    settings = get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        await initialize_runtime(application)
        try:
            yield
        finally:
            await shutdown_runtime(application)

    application = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=API_VERSION,
        openapi_tags=OPENAPI_TAGS,
        openapi_url=f"{settings.api_prefix}/openapi.json" if settings.docs_enabled else None,
        docs_url=f"{settings.api_prefix}/docs" if settings.docs_enabled else None,
        redoc_url=f"{settings.api_prefix}/redoc" if settings.docs_enabled else None,
        lifespan=lifespan,
    )

    # State initialization
    application.state.runtime_ready = False

    # Middleware Stack
    # (Middlewares added last execute first on requests, last on responses)
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(RequestTimingMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(SecurityHeadersMiddleware)

    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=[
                "Authorization",
                "Content-Type",
                "X-Request-ID",
                "X-Organization-ID",
                "X-User-ID",
                "Idempotency-Key",
                "If-Match",
                "*",
            ],
            expose_headers=[
                "X-Request-ID",
                "X-Response-Time-MS",
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining",
                "X-RateLimit-Reset",
                "Retry-After",
                "Idempotent-Replay",
            ],
        )

    # Centralized Exception Handlers (FCD-02 handlers first, FCD-07 API handlers supersede)
    register_exception_handlers(application)
    register_api_exception_handlers(application)

    # Versioned API Routers
    application.include_router(api_router, prefix=settings.api_prefix)

    return application
