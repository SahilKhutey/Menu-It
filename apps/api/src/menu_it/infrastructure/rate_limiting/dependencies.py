"""Rate limiting FastAPI dependencies (FCD-07 WP-10)."""

from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, Response, status

from menu_it.api.dependencies.request_context import get_client_ip
from menu_it.infrastructure.rate_limiting.limiter import (
    RateLimiter,
    default_rate_limiter,
)


def get_ip_rate_key(request: Request) -> str:
    """Build rate limit key based on client IP."""
    return f"ip:{get_client_ip(request)}"


def get_tenant_rate_key(request: Request) -> str:
    """Build rate limit key based on tenant organization ID if available, else fallback to IP."""
    tenant = getattr(request.state, "tenant_context", None)
    if tenant and getattr(tenant, "organization_id", None):
        return f"org:{tenant.organization_id}"
    return get_ip_rate_key(request)


def get_user_rate_key(request: Request) -> str:
    """Build rate limit key based on authenticated user ID if available, else fallback to IP."""
    principal = getattr(request.state, "authenticated_principal", None)
    if principal and getattr(principal, "user_id", None):
        return f"user:{principal.user_id}"
    return get_ip_rate_key(request)


def rate_limit(
    requests: int,
    window_seconds: int,
    key_builder: Callable[[Request], str] = get_ip_rate_key,
    limiter: RateLimiter | None = None,
) -> Any:
    """Dependency factory enforcing rate limits on endpoints.

    Sets standard X-RateLimit-* headers and raises HTTP 429 when exceeded.
    """
    active_limiter = limiter or default_rate_limiter

    async def _dependency(request: Request, response: Response) -> None:
        key = key_builder(request)
        result = await active_limiter.check_and_consume(
            key=key,
            limit=requests,
            window_seconds=window_seconds,
        )

        # Standard headers
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(result.reset_seconds)

        if not result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please retry after some time.",
                headers={
                    "Retry-After": str(result.reset_seconds),
                    "X-RateLimit-Limit": str(result.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(result.reset_seconds),
                },
            )

    return _dependency
