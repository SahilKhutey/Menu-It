"""Version 1 API router."""

from fastapi import APIRouter

from menu_it.api.v1.endpoints import (
    auth,
    branches,
    database_health,
    files,
    health,
    identity,
    internal_jobs,
    metrics,
    notifications,
    organizations,
    restaurant_configuration,
    sessions,
    system,
)
from menu_it.api.v1.modules.restaurants.router import router as restaurants_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(metrics.router, tags=["Observability"])
api_router.include_router(system.router, tags=["System"])
api_router.include_router(database_health.router, tags=["Database"])
api_router.include_router(files.router, tags=["Files"])
api_router.include_router(notifications.router, tags=["Notifications"])
api_router.include_router(internal_jobs.router, tags=["Internal Jobs & DLQ"])
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(identity.router, tags=["Identity"])
api_router.include_router(sessions.router, tags=["Sessions"])
api_router.include_router(organizations.router, tags=["Organizations"])
api_router.include_router(restaurants_router, prefix="/restaurants", tags=["Restaurants"])
api_router.include_router(branches.router, tags=["Branches"])
api_router.include_router(restaurant_configuration.router)
