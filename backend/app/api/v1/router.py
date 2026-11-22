"""
ModularMenu — API v1 Master Router Registration (ARC-07 §14.2).
Aggregates all domain API routers under /api/v1 prefix.
"""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    categories,
    customization,
    editor,
    items,
    licensing,
    media,
    menus,
    organizations,
    pricing,
    public,
    publishing,
    restaurants,
    themes,
)

v1_router = APIRouter()

# Register all capability group routers
v1_router.include_router(auth.router)
v1_router.include_router(organizations.router)
v1_router.include_router(restaurants.router)
v1_router.include_router(menus.router)
v1_router.include_router(categories.router)
v1_router.include_router(items.router)
v1_router.include_router(pricing.router)
v1_router.include_router(themes.router)
v1_router.include_router(customization.router)
v1_router.include_router(editor.router)
v1_router.include_router(publishing.router)
v1_router.include_router(media.router)
v1_router.include_router(public.router)
v1_router.include_router(licensing.router)
