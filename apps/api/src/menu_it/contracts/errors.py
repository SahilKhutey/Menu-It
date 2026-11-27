"""Standardized API error response contracts (FCD-06 §12.2)."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIErrorDetail(BaseModel):
    """Field-specific or constraint-specific error detail."""

    model_config = ConfigDict(frozen=True)

    field: str | None = None
    message: str
    code: str


class APIError(BaseModel):
    """Structured error payload envelope."""

    model_config = ConfigDict(frozen=True)

    code: str
    message: str
    details: list[dict[str, Any]] = Field(default_factory=list)
