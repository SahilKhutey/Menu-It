"""
ModularMenu — Request Context & Correlation (ARC-12 §30.2).
Provides thread-safe request correlation tracking.
"""

from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID

_correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    return _correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    _correlation_id_var.set(correlation_id)


@dataclass(frozen=True)
class RequestSecurityContext:
    user_id: UUID | None
    organization_id: UUID | None
    correlation_id: str
    client_ip: str
    is_authenticated: bool
