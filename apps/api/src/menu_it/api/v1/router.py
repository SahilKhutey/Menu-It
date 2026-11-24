"""Version 1 API router."""

from fastapi import APIRouter

from menu_it.api.v1.endpoints import database_health, health, organizations, system

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(system.router, tags=["System"])
api_router.include_router(database_health.router, tags=["Database"])
api_router.include_router(organizations.router, tags=["Organizations"])
