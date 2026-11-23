"""Version 1 API router."""

from fastapi import APIRouter

from menu_it.api.v1.endpoints import health, system

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(system.router, tags=["System"])
