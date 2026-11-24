"""Authenticated principal interface (FCD-04 §9.2)."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    """Trusted representation of the authenticated caller (FCD-05 §12.1)."""

    user_id: UUID
    session_id: UUID | None = None
    is_authenticated: bool = True
