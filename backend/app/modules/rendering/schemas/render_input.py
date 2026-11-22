"""
Pydantic Schemas for Render Validation and Input Checking (ARC-09 §11, WP-ARC09-11).
"""

from typing import Any

from pydantic import BaseModel, Field


class RenderValidationIssue(BaseModel):
    severity: str = "warning"  # error, warning, info
    code: str
    message: str
    path: str | None = None


class RenderValidationRequest(BaseModel):
    menu_id: str | None = None
    override_theme: dict[str, Any] | None = None
    override_layout: dict[str, Any] | None = None


class RenderValidationResponse(BaseModel):
    is_valid: bool
    total_issues: int = 0
    errors: list[RenderValidationIssue] = Field(default_factory=list)
    warnings: list[RenderValidationIssue] = Field(default_factory=list)
    render_readiness: str = "ready"  # ready, warnings, blocked
