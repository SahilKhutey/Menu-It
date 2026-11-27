"""System information endpoint."""

from fastapi import APIRouter

from menu_it.core.config import get_settings

router = APIRouter()


@router.get(
    "/system/info",
    summary="Non-Sensitive System Information",
)
async def system_information() -> dict[str, str]:
    """Return non-sensitive application metadata."""
    settings = get_settings()
    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "api_prefix": settings.api_prefix,
    }
