"""
ModularMenu — Request Correlation ID Middleware (ARC-12 §30.2).
Injects or validates X-Request-ID headers and establishes request context.
"""

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.request_context import set_correlation_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Generates a UUID4 request correlation ID if not present."""

    async def dispatch(self, request: Request, call_next) -> Response:
        incoming_id = request.headers.get("X-Request-ID")
        # Validate format or generate fresh UUID4
        request_id = incoming_id if incoming_id and len(incoming_id) <= 64 else str(uuid4())

        request.state.request_id = request_id
        set_correlation_id(request_id)

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
