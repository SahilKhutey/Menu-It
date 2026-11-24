"""Application startup and shutdown lifecycle (FCD-03 §11.2)."""

from fastapi import FastAPI

from menu_it.database.engine import engine


async def initialize_runtime(application: FastAPI) -> None:
    """Initialize application-level runtime resources."""
    application.state.runtime_ready = False
    application.state.runtime_ready = True


async def shutdown_runtime(application: FastAPI) -> None:
    """Release application-level runtime resources and dispose database engine."""
    application.state.runtime_ready = False
    await engine.dispose()
