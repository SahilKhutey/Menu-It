from fastapi import APIRouter
from app.api.v1 import auth, menus, platform, public, restaurants, themes, publishing

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(restaurants.router)
api_router.include_router(menus.router)
api_router.include_router(themes.router)
api_router.include_router(publishing.router)
api_router.include_router(public.router)
api_router.include_router(platform.router)
