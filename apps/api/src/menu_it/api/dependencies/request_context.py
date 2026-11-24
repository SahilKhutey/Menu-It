"""Request context extraction dependencies (FCD-07 §11.2)."""

from uuid import uuid4

from fastapi import Request


def get_request_id(request: Request) -> str:
    """Extract or generate request correlation ID."""
    rid = getattr(request.state, "request_id", None)
    return str(rid) if rid else str(uuid4())


def get_client_ip(request: Request) -> str:
    """Extract client IP address handling forwarded proxies safely."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
        if client_ip:
            return client_ip
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"
