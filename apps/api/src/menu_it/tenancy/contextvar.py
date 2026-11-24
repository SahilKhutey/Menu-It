"""ContextVar-based request-scoped tenant context storage (FCD-04 §8.2)."""

from contextvars import ContextVar, Token

from menu_it.tenancy.context import TenantContext

_current_tenant: ContextVar[TenantContext | None] = ContextVar("current_tenant", default=None)


def set_current_tenant(context: TenantContext) -> Token:
    """Set request-scoped tenant context."""
    return _current_tenant.set(context)


def get_current_tenant() -> TenantContext:
    """Retrieve active tenant context; raises RuntimeError if not set."""
    context = _current_tenant.get()
    if context is None:
        raise RuntimeError("Tenant context has not been established")
    return context


def reset_current_tenant(token: Token) -> None:
    """Reset tenant context token after request/task completion."""
    _current_tenant.reset(token)
