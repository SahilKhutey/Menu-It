"""Auth package exports (FCD-04 §9, §10)."""

from menu_it.auth.dependencies import get_current_principal
from menu_it.auth.principal import AuthenticatedPrincipal

__all__ = [
    "AuthenticatedPrincipal",
    "get_current_principal",
]
