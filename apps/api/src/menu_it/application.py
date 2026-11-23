"""Application factory for the Menu-It API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from menu_it.api.v1.router import api_router
from menu_it.core.config import get_settings
from menu_it.core.lifecycle import initialize_runtime, shutdown_runtime
from menu_it.core.logging import configure_logging
from menu_it.core.metadata import API_VERSION, APP_DESCRIPTION, APP_TITLE
from menu_it.exceptions.handlers import register_exception_handlers
from menu_it.middleware.request_id import RequestIDMiddleware


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
        openapi_url=f"{settings.api_prefix}/openapi.json" if settings.docs_enabled else None,
        docs_url=f"{settings.api_prefix}/docs" if settings.docs_enabled else None,
        redoc_url=f"{settings.api_prefix}/redoc" if settings.docs_enabled else None,
        lifespan=lifespan,
    )

    # State initialization
    application.state.runtime_ready = False

    # Middlewares (Starlette executes middlewares added last first:
    # RequestID is innermost, CORSMiddleware is outermost)
    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    application.add_middleware(RequestIDMiddleware)

    # Exception Handlers
    register_exception_handlers(application)

    # Routers
    application.include_router(api_router, prefix=settings.api_prefix)

    return application
