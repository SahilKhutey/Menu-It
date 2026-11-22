"""
ModularMenu — Editor & Preview API Schemas (ARC-07 §4.7).
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EditorStateSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    draft_payload: dict[str, Any]
    row_version: int = Field(ge=1)


class EditorStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    menu_id: UUID
    restaurant_id: UUID
    organization_id: UUID
    draft_payload: dict[str, Any]
    row_version: int
    is_dirty: bool = False


class PreviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    menu_id: UUID
    restaurant_name: str
    theme_tokens: dict[str, Any]
    layout: dict[str, Any]
    categories: list[dict[str, Any]]
    items: list[dict[str, Any]]
    preview_url: str


class ValidationErrorItem(BaseModel):
    field: str
    code: str
    message: str


class ValidationReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    is_valid: bool
    errors: list[ValidationErrorItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
