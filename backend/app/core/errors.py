from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel


class ProblemDetails(BaseModel):
    """RFC 7807 Problem Details representation."""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    invalid_params: Optional[list] = None


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Formats HTTPException into RFC 7807 problem details format."""
    status_code = exc.status_code
    title_map = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
    }
    title = title_map.get(status_code, "HTTP Error")
    error_type = f"https://errors.modularmenu.in/{title.lower().replace(' ', '-')}"

    content = {
        "type": error_type,
        "title": title,
        "status": status_code,
        "detail": str(exc.detail),
        "instance": request.url.path,
    }

    return JSONResponse(
        status_code=status_code,
        content=content,
        headers={"Content-Type": "application/problem+json"}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Formats validation errors into RFC 7807 format."""
    content = {
        "type": "https://errors.modularmenu.in/validation-error",
        "title": "Validation Error",
        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "detail": "Request payload failed schema validation",
        "instance": request.url.path,
        "invalid_params": exc.errors()
    }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=content,
        headers={"Content-Type": "application/problem+json"}
    )
