"""Unit tests for application runtime lifecycle."""

import pytest
from fastapi import FastAPI

from menu_it.core.lifecycle import (
    initialize_runtime,
    shutdown_runtime,
)


@pytest.mark.asyncio
async def test_runtime_initialization():
    """Verify runtime initialization sets state to ready."""
    app = FastAPI()
    await initialize_runtime(app)
    assert app.state.runtime_ready is True


@pytest.mark.asyncio
async def test_runtime_shutdown():
    """Verify runtime shutdown marks state as not ready."""
    app = FastAPI()
    await initialize_runtime(app)
    await shutdown_runtime(app)
    assert app.state.runtime_ready is False


@pytest.mark.asyncio
async def test_runtime_reinitialization():
    """Verify runtime lifecycle can be safely executed repeatedly."""
    app = FastAPI()
    await initialize_runtime(app)
    await shutdown_runtime(app)
    await initialize_runtime(app)
    assert app.state.runtime_ready is True
