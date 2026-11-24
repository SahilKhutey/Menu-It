"""Authenticated principal interface (FCD-04 §9.2)."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    """Trusted representation of the authenticated caller."""

    user_id: UUID
    is_authenticated: bool = True
