"""Request correlation ID middleware."""

from uuid import UUID, uuid4

from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assign a validated request ID to every request."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        incoming_id = request.headers.get("X-Request-ID")
        try:
            request_id = UUID(incoming_id) if incoming_id else uuid4()
        except (ValueError, TypeError, AttributeError):
            request_id = uuid4()

        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = str(request_id)
        return response
