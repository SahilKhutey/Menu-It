"""
ModularMenu — RFC 9457 / RFC 7807 Problem Details and Exception Mapping (ARC-07 §5.5, §14.6).
Provides consistent, machine-readable error responses with zero stack trace or internal credential leaks.
"""
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ProblemDetails(BaseModel):
    """RFC 7807 / RFC 9457 Problem Details representation."""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    code: Optional[str] = None
    request_id: Optional[str] = None
    invalid_params: Optional[list] = None
    errors: Optional[list] = None


# Domain / Application Exception Classes
class ApiBaseException(Exception):
    def __init__(self, detail: str, code: Optional[str] = None):
        super().__init__(detail)
        self.detail = detail
        self.code = code


class ResourceNotFoundError(ApiBaseException):
    def __init__(self, detail: str = "Resource not found", code: str = "RESOURCE_NOT_FOUND"):
        super().__init__(detail=detail, code=code)


class PermissionDeniedError(ApiBaseException):
    def __init__(self, detail: str = "Permission denied", code: str = "PERMISSION_DENIED"):
        super().__init__(detail=detail, code=code)


class AuthenticationRequiredError(ApiBaseException):
    def __init__(self, detail: str = "Authentication required", code: str = "AUTHENTICATION_REQUIRED"):
        super().__init__(detail=detail, code=code)


class ConflictError(ApiBaseException):
    def __init__(self, detail: str = "Resource state conflict", code: str = "RESOURCE_CONFLICT"):
        super().__init__(detail=detail, code=code)


class ConcurrencyConflictError(ApiBaseException):
    def __init__(self, detail: str = "Concurrency version conflict: stale update rejected", code: str = "VERSION_CONFLICT"):
        super().__init__(detail=detail, code=code)


class IdempotencyConflictError(ApiBaseException):
    def __init__(self, detail: str = "Idempotency key reused with different request payload", code: str = "IDEMPOTENCY_CONFLICT"):
        super().__init__(detail=detail, code=code)


class RateLimitExceededError(ApiBaseException):
    def __init__(self, detail: str = "Rate limit exceeded. Please retry later.", retry_after: int = 30, code: str = "RATE_LIMIT_EXCEEDED"):
        super().__init__(detail=detail, code=code)
        self.retry_after = retry_after


class UploadTooLargeError(ApiBaseException):
    def __init__(self, detail: str = "Payload exceeds size limit", code: str = "UPLOAD_TOO_LARGE"):
        super().__init__(detail=detail, code=code)


class UnsupportedMediaTypeError(ApiBaseException):
    def __init__(self, detail: str = "Unsupported media type", code: str = "UNSUPPORTED_MEDIA_TYPE"):
        super().__init__(detail=detail, code=code)


class DependencyUnavailableError(ApiBaseException):
    def __init__(self, detail: str = "Required upstream dependency unavailable", code: str = "DEPENDENCY_UNAVAILABLE"):
        super().__init__(detail=detail, code=code)


def _build_problem_response(
    status_code: int,
    title: str,
    detail: str,
    instance: str,
    code: str,
    request_id: Optional[str] = None,
    errors: Optional[list] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    error_slug = title.lower().replace(" ", "-")
    error_type = f"https://errors.modularmenu.in/{error_slug}"

    content: Dict[str, Any] = {
        "type": error_type,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
        "code": code,
    }
    if request_id:
        content["request_id"] = request_id
    if errors:
        content["errors"] = errors
        content["invalid_params"] = errors

    headers = {"Content-Type": "application/problem+json"}
    if request_id:
        headers["X-Request-ID"] = request_id
    if extra_headers:
        headers.update(extra_headers)

    return JSONResponse(status_code=status_code, content=content, headers=headers)


# HTTP Exception Handler
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    status_code = exc.status_code
    title_map = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        412: "Precondition Failed",
        413: "Payload Too Large",
        415: "Unsupported Media Type",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        503: "Service Unavailable",
    }
    code_map = {
        400: "BAD_REQUEST",
        401: "AUTHENTICATION_REQUIRED",
        403: "PERMISSION_DENIED",
        404: "RESOURCE_NOT_FOUND",
        409: "RESOURCE_CONFLICT",
        412: "VERSION_CONFLICT",
        413: "UPLOAD_TOO_LARGE",
        415: "UNSUPPORTED_MEDIA_TYPE",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
        503: "DEPENDENCY_UNAVAILABLE",
    }
    title = title_map.get(status_code, "HTTP Error")
    code = code_map.get(status_code, "HTTP_ERROR")
    request_id = getattr(request.state, "request_id", None)

    extra_headers = {}
    if exc.headers:
        extra_headers.update(exc.headers)

    return _build_problem_response(
        status_code=status_code,
        title=title,
        detail=str(exc.detail),
        instance=request.url.path,
        code=code,
        request_id=request_id,
        extra_headers=extra_headers,
    )


# Request Validation Exception Handler
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    formatted_errors = []
    for err in exc.errors():
        loc = ".".join(str(l) for l in err.get("loc", []))
        formatted_errors.append({
            "field": loc,
            "code": err.get("type", "INVALID"),
            "message": err.get("msg", "Invalid field"),
        })

    return _build_problem_response(
        status_code=422,
        title="Validation Error",
        detail="Request payload failed schema validation",
        instance=request.url.path,
        code="VALIDATION_ERROR",
        request_id=request_id,
        errors=formatted_errors,
    )


def register_error_handlers(app: FastAPI) -> None:
    """Registers all exception handlers on the FastAPI application (ARC-07 §14.6)."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    @app.exception_handler(ResourceNotFoundError)
    async def not_found_handler(request: Request, exc: ResourceNotFoundError):
        return _build_problem_response(
            status_code=404,
            title="Not Found",
            detail=exc.detail,
            instance=request.url.path,
            code=exc.code or "RESOURCE_NOT_FOUND",
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
        return _build_problem_response(
            status_code=403,
            title="Forbidden",
            detail=exc.detail,
            instance=request.url.path,
            code=exc.code or "PERMISSION_DENIED",
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(AuthenticationRequiredError)
    async def auth_required_handler(request: Request, exc: AuthenticationRequiredError):
        return _build_problem_response(
            status_code=401,
            title="Unauthorized",
            detail=exc.detail,
            instance=request.url.path,
            code=exc.code or "AUTHENTICATION_REQUIRED",
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return _build_problem_response(
            status_code=409,
            title="Conflict",
            detail=exc.detail,
            instance=request.url.path,
            code=exc.code or "RESOURCE_CONFLICT",
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(ConcurrencyConflictError)
    async def concurrency_handler(request: Request, exc: ConcurrencyConflictError):
        return _build_problem_response(
            status_code=409,
            title="Conflict",
            detail=exc.detail,
            instance=request.url.path,
            code=exc.code or "VERSION_CONFLICT",
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(IdempotencyConflictError)
    async def idempotency_handler(request: Request, exc: IdempotencyConflictError):
        return _build_problem_response(
            status_code=409,
            title="Conflict",
            detail=exc.detail,
            instance=request.url.path,
            code=exc.code or "IDEMPOTENCY_CONFLICT",
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_handler(request: Request, exc: RateLimitExceededError):
        return _build_problem_response(
            status_code=429,
            title="Too Many Requests",
            detail=exc.detail,
            instance=request.url.path,
            code=exc.code or "RATE_LIMIT_EXCEEDED",
            request_id=getattr(request.state, "request_id", None),
            extra_headers={"Retry-After": str(exc.retry_after)},
        )

    @app.exception_handler(UploadTooLargeError)
    async def upload_too_large_handler(request: Request, exc: UploadTooLargeError):
        return _build_problem_response(
            status_code=413,
            title="Payload Too Large",
            detail=exc.detail,
            instance=request.url.path,
            code=exc.code or "UPLOAD_TOO_LARGE",
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(UnsupportedMediaTypeError)
    async def unsupported_media_handler(request: Request, exc: UnsupportedMediaTypeError):
        return _build_problem_response(
            status_code=415,
            title="Unsupported Media Type",
            detail=exc.detail,
            instance=request.url.path,
            code=exc.code or "UNSUPPORTED_MEDIA_TYPE",
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(DependencyUnavailableError)
    async def dependency_unavailable_handler(request: Request, exc: DependencyUnavailableError):
        return _build_problem_response(
            status_code=503,
            title="Service Unavailable",
            detail=exc.detail,
            instance=request.url.path,
            code=exc.code or "DEPENDENCY_UNAVAILABLE",
            request_id=getattr(request.state, "request_id", None),
        )
