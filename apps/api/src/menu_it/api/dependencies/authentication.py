"""Authentication dependencies for API endpoints (FCD-07 §12.2)."""

from menu_it.auth.dependencies import get_current_principal
from menu_it.auth.principal import AuthenticatedPrincipal

# Primary dependency alias
get_authenticated_principal = get_current_principal

__all__ = [
    "AuthenticatedPrincipal",
    "get_authenticated_principal",
    "get_current_principal",
]
