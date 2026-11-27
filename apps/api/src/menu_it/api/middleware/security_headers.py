"""Comprehensive security response headers middleware (FCD-07 §11.4 & FCD-11 WP-05)."""

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware:
    """Inject hardened security response headers into HTTP responses."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        enable_hsts: bool = True,
        hsts_max_age: int = 31536000,
        include_subdomains: bool = True,
        hsts_preload: bool = False,
    ) -> None:
        self.app = app
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        self.include_subdomains = include_subdomains
        self.hsts_preload = hsts_preload

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        is_https = scope.get("scheme") == "https"
        headers_in = dict(scope.get("headers", []))
        if not is_https and headers_in.get(b"x-forwarded-proto") == b"https":
            is_https = True

        async def add_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                existing = {key.lower() for key, _ in headers}

                standard_headers: dict[bytes, bytes] = {
                    b"x-content-type-options": b"nosniff",
                    b"referrer-policy": b"strict-origin-when-cross-origin",
                    b"x-frame-options": b"DENY",
                    b"permissions-policy": b"geolocation=(), camera=(), microphone=(), payment=()",
                    b"cross-origin-opener-policy": b"same-origin",
                    b"cross-origin-resource-policy": b"same-site",
                    b"content-security-policy": (
                        b"default-src 'self'; frame-ancestors 'none'; "
                        b"object-src 'none'; base-uri 'self'"
                    ),
                }

                if self.enable_hsts and is_https:
                    hsts_val = f"max-age={self.hsts_max_age}"
                    if self.include_subdomains:
                        hsts_val += "; includeSubDomains"
                    if self.hsts_preload:
                        hsts_val += "; preload"
                    standard_headers[b"strict-transport-security"] = hsts_val.encode("ascii")

                for key, value in standard_headers.items():
                    if key not in existing:
                        headers.append((key, value))

                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, add_headers)
