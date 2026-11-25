"""Application startup and shutdown lifecycle (FCD-03 §11.2, FCD-09 WP-07)."""

from fastapi import FastAPI

from menu_it.database.engine import engine
from menu_it.platform.container import build_platform_services


async def initialize_runtime(application: FastAPI) -> None:
    """Initialize application-level runtime resources and platform services."""
    application.state.runtime_ready = False

    # Initialize Platform Services Container
    platform_services = build_platform_services()
    application.state.platform_services = platform_services

    application.state.runtime_ready = True


async def shutdown_runtime(application: FastAPI) -> None:
    """Release application-level runtime resources and dispose database engine."""
    application.state.runtime_ready = False
    await engine.dispose()
