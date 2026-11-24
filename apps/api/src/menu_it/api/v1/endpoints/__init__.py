"""API v1 endpoints."""

from menu_it.api.v1.endpoints import (
    auth,
    database_health,
    health,
    identity,
    organizations,
    sessions,
    system,
)

__all__ = [
    "auth",
    "database_health",
    "health",
    "identity",
    "organizations",
    "sessions",
    "system",
]
