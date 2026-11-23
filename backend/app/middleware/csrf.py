"""
ModularMenu — CSRF Protection Middleware & Guard (ARC-12 §7.4).
Enforces CSRF token validation on cookie-authenticated state-changing requests.
"""

import hmac

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
EXEMPT_PATHS = frozenset(
    {
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/logout",
        "/api/v1/auth/password/forgot",
        "/api/v1/auth/password/reset",
        "/api/v1/webhooks",
        "/api/v1/public",
        "/health",
        "/health/live",
        "/health/ready",
        "/health/startup",
        "/docs",
        "/openapi.json",
    }
)


def verify_csrf_token(expected_token: str | None, supplied_token: str | None) -> bool:
    """Constant-time comparison of CSRF tokens."""
    if not expected_token or not supplied_token:
        return False
    return hmac.compare_digest(expected_token, supplied_token)


class CSRFMiddleware(BaseHTTPMiddleware):
    """Validates X-CSRF-Token on unsafe requests that carry session cookies."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in SAFE_METHODS:
            return await call_next(request)

        # Skip exempt or public endpoints
        if any(request.url.path.startswith(path) for path in EXEMPT_PATHS):
            return await call_next(request)

        # Requests authenticated with Bearer tokens are API calls, exempt from CSRF
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            return await call_next(request)

        # If request is cookie-authenticated, require CSRF token
        session_cookie = request.cookies.get("__Host-modularmenu_session") or request.cookies.get(
            "modularmenu_session"
        )
        if session_cookie:
            csrf_token = request.headers.get("X-CSRF-Token")
            expected_csrf = request.cookies.get("csrf_token") or getattr(
                request.state, "csrf_token", None
            )

            if not csrf_token or not verify_csrf_token(expected_csrf, csrf_token):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF validation failed"},
                )

        return await call_next(request)
