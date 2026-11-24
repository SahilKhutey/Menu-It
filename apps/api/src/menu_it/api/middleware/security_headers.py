"""Security response headers middleware (FCD-07 §11.4)."""

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware:
    """Inject standard security response headers into HTTP responses."""

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

        async def add_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                existing = {key.lower() for key, _ in headers}

                security_headers = {
                    b"x-content-type-options": b"nosniff",
                    b"referrer-policy": b"strict-origin-when-cross-origin",
                    b"x-frame-options": b"DENY",
                }

                for key, value in security_headers.items():
                    if key not in existing:
                        headers.append((key, value))

                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, add_headers)
