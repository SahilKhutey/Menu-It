"""Standard API response factory helpers (FCD-07 §8.1)."""

from datetime import UTC, datetime
from typing import Any

from starlette.responses import JSONResponse

from menu_it.api.schemas.common import (
    APIError,
    APIErrorDetail,
    APIResponse,
    ResponseMeta,
)


def success_response(
    *,
    data: Any,
    request_id: str,
) -> APIResponse[Any]:
    """Construct an enveloped APIResponse on success."""
    return APIResponse(
        success=True,
        data=data,
        error=None,
        meta=ResponseMeta(
            request_id=request_id,
            timestamp=datetime.now(UTC),
        ),
    )


def error_response(
    *,
    code: str,
    message: str,
    request_id: str,
    details: list[APIErrorDetail] | None = None,
) -> APIResponse[None]:
    """Construct an enveloped APIResponse on failure."""
    return APIResponse(
        success=False,
        data=None,
        error=APIError(
            code=code,
            message=message,
            details=details or [],
        ),
        meta=ResponseMeta(
            request_id=request_id,
            timestamp=datetime.now(UTC),
        ),
    )


def json_error_response(
    *,
    code: str,
    message: str,
    request_id: str,
    status_code: int,
    details: list[dict[str, Any]] | list[APIErrorDetail] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Construct an enveloped Starlette JSONResponse with X-Request-ID header."""
    response_headers = {"X-Request-ID": request_id}
    if headers:
        response_headers.update(headers)

    normalized_details: list[dict[str, Any]] = []
    if details:
        for item in details:
            if isinstance(item, APIErrorDetail):
                normalized_details.append(item.model_dump())
            elif isinstance(item, dict):
                normalized_details.append(item)

    return JSONResponse(
        status_code=status_code,
        headers=response_headers,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": normalized_details,
            },
            "meta": {
                "request_id": request_id,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        },
    )
