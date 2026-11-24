"""Request correlation ID middleware (FCD-07 §11.2)."""

from uuid import UUID, uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestIDMiddleware:
    """Ensure every HTTP request has a validated UUID correlation request ID."""

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

        headers = dict(scope.get("headers", []))
        supplied_id = (
            headers.get(b"x-request-id", b"")
            .decode(
                "ascii",
                errors="ignore",
            )
            .strip()
        )

        # Enforce UUID format: if invalid or absent, generate new UUID4
        try:
            validated_id = UUID(supplied_id) if supplied_id else uuid4()
        except (ValueError, TypeError, AttributeError):
            validated_id = uuid4()

        request_id_str = str(validated_id)

        # Store in scope state (accessible as request.state.request_id)
        state = scope.setdefault("state", {})
        state["request_id"] = validated_id

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                resp_headers = list(message.get("headers", []))
                filtered = [(k, v) for k, v in resp_headers if k.lower() != b"x-request-id"]
                filtered.append((b"x-request-id", request_id_str.encode("ascii")))
                message = {**message, "headers": filtered}
            await send(message)

        await self.app(scope, receive, send_with_request_id)
