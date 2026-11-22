"""
Domain Exceptions for Menu Rendering (ARC-09 §11, WP-ARC09-11).
RFC 7807 problem details mappings and render error definitions.
"""
from typing import Any, Dict, Optional


class RenderError(Exception):
    """Base domain exception for all menu rendering failures."""
    def __init__(self, message: str, code: str = "RENDER_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class RenderInputValidationError(RenderError):
    """Raised when the render input DTO fails structural or semantic validation."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="RENDER_INPUT_VALIDATION_ERROR", details=details)


class RenderComponentNotFoundError(RenderError):
    """Raised when a component specified in the layout or plan is not registered in the catalogue."""
    def __init__(self, component_name: str, slot: Optional[str] = None):
        super().__init__(
            f"Component '{component_name}' not found in component registry",
            code="RENDER_COMPONENT_NOT_FOUND",
            details={"component_name": component_name, "slot": slot},
        )


class RenderLayoutCompatibilityError(RenderError):
    """Raised when a selected layout is incompatible with the restaurant's theme or content."""
    def __init__(self, layout_type: str, reason: str):
        super().__init__(
            f"Layout '{layout_type}' is incompatible: {reason}",
            code="RENDER_LAYOUT_INCOMPATIBLE",
            details={"layout_type": layout_type, "reason": reason},
        )


class RenderThemeCompatibilityError(RenderError):
    """Raised when theme tokens fail schema constraints or required tokens are missing."""
    def __init__(self, theme_id: str, missing_tokens: list[str]):
        super().__init__(
            f"Theme '{theme_id}' is missing required tokens: {', '.join(missing_tokens)}",
            code="RENDER_THEME_INCOMPATIBLE",
            details={"theme_id": theme_id, "missing_tokens": missing_tokens},
        )


class RenderPriceInvalidError(RenderError):
    """Raised when price values fail precision, negative-check, or currency rules."""
    def __init__(self, item_name: str, price: Any, reason: str):
        super().__init__(
            f"Price for item '{item_name}' ({price}) is invalid: {reason}",
            code="RENDER_PRICE_INVALID",
            details={"item_name": item_name, "price": str(price), "reason": reason},
        )


class RenderSnapshotNotFoundError(RenderError):
    """Raised when an active published snapshot cannot be found for public delivery."""
    def __init__(self, restaurant_slug: str, menu_slug: str):
        super().__init__(
            f"No published snapshot found for restaurant '{restaurant_slug}' and menu '{menu_slug}'",
            code="RENDER_SNAPSHOT_NOT_FOUND",
            details={"restaurant_slug": restaurant_slug, "menu_slug": menu_slug},
        )


class RenderMediaNotFoundError(RenderError):
    """Raised when a required media asset cannot be resolved and no fallback exists."""
    def __init__(self, asset_id: str, slot: str):
        super().__init__(
            f"Media asset '{asset_id}' for slot '{slot}' not found",
            code="RENDER_MEDIA_NOT_FOUND",
            details={"asset_id": asset_id, "slot": slot},
        )
