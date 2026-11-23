"""Shared test fixtures for the Menu-It backend API."""

import pytest
from fastapi.testclient import TestClient

from menu_it.application import create_application


@pytest.fixture
def app():
    """Create a fresh FastAPI application instance for testing."""
    return create_application()


@pytest.fixture
def client(app):
    """Provide a TestClient within the application lifespan context."""
    with TestClient(app) as test_client:
        yield test_client
