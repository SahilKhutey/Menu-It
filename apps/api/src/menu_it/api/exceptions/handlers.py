"""Centralized API exception handlers (FCD-07 §10.3)."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from menu_it.api.dependencies.request_context import get_request_id
from menu_it.api.exceptions.mapping import map_domain_error
from menu_it.api.exceptions.responses import json_error_response
from menu_it.api.schemas.common import APIErrorDetail
from menu_it.api.schemas.errors import ErrorCode
from menu_it.domain.base.errors import DomainError
from menu_it.infrastructure.idempotency.exceptions import (
    IdempotencyConflictError,
    IdempotentReplayException,
)

logger = logging.getLogger(__name__)


def normalize_validation_error(error: dict[str, Any]) -> APIErrorDetail:
    """Normalize Pydantic validation error into stable APIErrorDetail without value leakage."""
    loc = error.get("loc", [])
    # Strip leading 'body', 'query', or 'path' if present for clean field path
    field_parts = [str(x) for x in loc if x not in ("body", "query", "path")]
    field_name = ".".join(field_parts) if field_parts else None
    err_type = str(error.get("type", "invalid_value"))
    err_msg = str(error.get("msg", "Invalid value provided."))

    return APIErrorDetail(
        field=field_name,
        code=err_type,
        message=err_msg,
    )


def register_api_exception_handlers(app: FastAPI) -> None:
    """Register centralized exception handlers on the FastAPI application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        rid = get_request_id(request)
        details = [normalize_validation_error(err) for err in exc.errors()]
        return json_error_response(
            code=ErrorCode.VALIDATION_ERROR.value,
            message="The request contains invalid fields.",
            request_id=rid,
            status_code=422,
            details=details,
        )

    @app.exception_handler(HTTPException)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        rid = get_request_id(request)
        headers = dict(exc.headers) if exc.headers else None

        # Compatibility with legacy FCD-02 non-prefixed test routes
        if not request.url.path.startswith("/api/"):
            return json_error_response(
                code="HTTP_ERROR",
                message=str(exc.detail),
                request_id=rid,
                status_code=exc.status_code,
                headers=headers,
            )

        code = ErrorCode.INTERNAL_ERROR.value
        if exc.status_code == 401:
            code = ErrorCode.AUTHENTICATION_REQUIRED.value
        elif exc.status_code == 403:
            code = ErrorCode.PERMISSION_DENIED.value
        elif exc.status_code == 404:
            code = ErrorCode.RESOURCE_NOT_FOUND.value
        elif exc.status_code == 409:
            code = ErrorCode.RESOURCE_CONFLICT.value
        elif exc.status_code == 412:
            code = ErrorCode.PRECONDITION_FAILED.value
        elif exc.status_code == 422:
            code = ErrorCode.VALIDATION_ERROR.value
        elif exc.status_code == 429:
            code = ErrorCode.RATE_LIMIT_EXCEEDED.value
        elif exc.status_code == 503:
            code = ErrorCode.SERVICE_UNAVAILABLE.value

        return json_error_response(
            code=code,
            message=str(exc.detail),
            request_id=rid,
            status_code=exc.status_code,
            headers=headers,
        )

    @app.exception_handler(IdempotentReplayException)
    async def idempotent_replay_handler(
        request: Request,
        exc: IdempotentReplayException,
    ) -> JSONResponse:
        rid = get_request_id(request)
        headers = {
            "X-Request-ID": rid,
            "Idempotent-Replay": "true",
            "X-Cache-Lookup": "HIT",
        }
        return JSONResponse(
            status_code=exc.status_code,
            headers=headers,
            content=exc.response_body,
        )

    @app.exception_handler(IdempotencyConflictError)
    async def idempotency_conflict_handler(
        request: Request,
        exc: IdempotencyConflictError,
    ) -> JSONResponse:
        rid = get_request_id(request)
        return json_error_response(
            code=ErrorCode.IDEMPOTENCY_CONFLICT.value,
            message=exc.message,
            request_id=rid,
            status_code=409,
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        rid = get_request_id(request)
        mapping = map_domain_error(exc)
        return json_error_response(
            code=mapping.error_code.value,
            message=str(exc),
            request_id=rid,
            status_code=mapping.status_code,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        rid = get_request_id(request)
        logger.error(
            "Unhandled server exception occurred. Request ID: %s",
            rid,
            exc_info=exc,
        )
        code = (
            "INTERNAL_SERVER_ERROR"
            if not request.url.path.startswith("/api/")
            else ErrorCode.INTERNAL_ERROR.value
        )
        return json_error_response(
            code=code,
            message="An unexpected server error occurred.",
            request_id=rid,
            status_code=500,
        )
