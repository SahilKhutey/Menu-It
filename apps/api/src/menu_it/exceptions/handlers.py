"""Centralized API exception handlers."""

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    """Extract or generate a string request ID from the request state."""
    request_id = getattr(request.state, "request_id", None)
    if isinstance(request_id, UUID):
        return str(request_id)
    return str(request_id) if request_id else str(uuid4())


def error_response(
    request: Request,
    code: str,
    message: str,
    status_code: int,
    details: list[dict[str, object]] | None = None,
) -> JSONResponse:
    """Construct standard enveloped JSON error response adhering to API specifications."""
    request_id = get_request_id(request)
    headers = {"X-Request-ID": request_id}
    return JSONResponse(
        status_code=status_code,
        headers=headers,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
            },
            "meta": {
                "request_id": request_id,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register centralized error handlers on the FastAPI application."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return error_response(
            request=request,
            code="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            {
                "loc": list(err.get("loc", [])),
                "msg": str(err.get("msg", "")),
                "type": str(err.get("type", "")),
            }
            for err in exc.errors()
        ]
        return error_response(
            request=request,
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            status_code=422,
            details=errors,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = get_request_id(request)
        logger.error(
            "Unhandled server exception occurred. Request ID: %s",
            request_id,
            exc_info=exc,
        )
        return error_response(
            request=request,
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred.",
            status_code=500,
        )
