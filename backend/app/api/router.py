"""
ModularMenu — Root API Router (ARC-03 §4.3, ARC-07 §14.2).
Mounts API version routers under their respective prefixes.
"""

from fastapi import APIRouter

from app.api.v1 import platform
from app.api.v1.router import v1_router

api_router = APIRouter()

# Mount v1 routers
api_router.include_router(v1_router)
api_router.include_router(platform.router)
