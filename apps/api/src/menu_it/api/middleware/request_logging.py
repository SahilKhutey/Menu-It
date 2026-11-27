"""Safe request logging middleware with sensitive parameter redaction (FCD-07 §11.1)."""

import logging

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("menu_it.access")

SENSITIVE_HEADERS = {
    b"authorization",
    b"cookie",
    b"set-cookie",
    b"x-api-key",
}


class RequestLoggingMiddleware:
    """Log incoming HTTP requests with safety redaction."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "")
        rid = scope.get("state", {}).get("request_id", "unknown")

        async def send_with_logging(message: Message) -> None:
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                logger.info(
                    "%s %s -> %s [request_id=%s]",
                    method,
                    path,
                    status_code,
                    rid,
                )
            await send(message)

        await self.app(scope, receive, send_with_logging)
