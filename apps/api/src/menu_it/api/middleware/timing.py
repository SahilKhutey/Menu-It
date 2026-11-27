"""Request execution timing middleware (FCD-07 §11.3)."""

import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestTimingMiddleware:
    """Measure request duration and inject X-Response-Time-MS header."""

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

        started = time.perf_counter()

        async def send_with_timing(message: Message) -> None:
            if message["type"] == "http.response.start":
                elapsed_ms = (time.perf_counter() - started) * 1000
                headers = list(message.get("headers", []))
                headers.append(
                    (
                        b"x-response-time-ms",
                        f"{elapsed_ms:.2f}".encode("ascii"),
                    )
                )
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_timing)
