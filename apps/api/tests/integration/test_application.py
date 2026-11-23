"""Integration tests for application factory and metadata."""

from fastapi import FastAPI

from menu_it.application import create_application


def test_application_factory():
    """Verify application factory creates a valid FastAPI instance."""
    app = create_application()
    assert isinstance(app, FastAPI)


def test_application_metadata():
    """Verify application instance carries correct metadata."""
    app = create_application()
    assert app.title == "Menu-It API"
    assert app.version == "0.1.0"


def test_application_routes_registered():
    """Verify core routes are registered under /api/v1."""
    app = create_application()
    paths = set(app.openapi()["paths"].keys())
    assert "/api/v1/health" in paths
    assert "/api/v1/health/live" in paths
    assert "/api/v1/health/ready" in paths
    assert "/api/v1/system/info" in paths
