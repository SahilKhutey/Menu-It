"""Application startup and shutdown lifecycle."""

from fastapi import FastAPI


async def initialize_runtime(application: FastAPI) -> None:
    """Initialize application-level runtime resources."""
    application.state.runtime_ready = False
    # FCD-02: No external infrastructure is required here yet.
    # Future phases:
    # FCD-03: Database initialization.
    # FCD-09: Shared service initialization.
    # FCD-10: Worker and event infrastructure.
    application.state.runtime_ready = True


async def shutdown_runtime(application: FastAPI) -> None:
    """Release application-level runtime resources."""
    application.state.runtime_ready = False
