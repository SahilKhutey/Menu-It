"""
ModularMenu — Editor & Preview API Schemas (ARC-07 §4.7).
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class EditorStateSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    draft_payload: Dict[str, Any]
    row_version: int = Field(ge=1)


class EditorStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    menu_id: UUID
    restaurant_id: UUID
    organization_id: UUID
    draft_payload: Dict[str, Any]
    row_version: int
    is_dirty: bool = False


class PreviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    menu_id: UUID
    restaurant_name: str
    theme_tokens: Dict[str, Any]
    layout: Dict[str, Any]
    categories: List[Dict[str, Any]]
    items: List[Dict[str, Any]]
    preview_url: str


class ValidationErrorItem(BaseModel):
    field: str
    code: str
    message: str


class ValidationReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    is_valid: bool
    errors: List[ValidationErrorItem] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
