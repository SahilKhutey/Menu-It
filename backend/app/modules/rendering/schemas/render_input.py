"""
Pydantic Schemas for Render Validation and Input Checking (ARC-09 §11, WP-ARC09-11).
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RenderValidationIssue(BaseModel):
    severity: str = "warning"  # error, warning, info
    code: str
    message: str
    path: Optional[str] = None


class RenderValidationRequest(BaseModel):
    menu_id: Optional[str] = None
    override_theme: Optional[Dict[str, Any]] = None
    override_layout: Optional[Dict[str, Any]] = None


class RenderValidationResponse(BaseModel):
    is_valid: bool
    total_issues: int = 0
    errors: List[RenderValidationIssue] = Field(default_factory=list)
    warnings: List[RenderValidationIssue] = Field(default_factory=list)
    render_readiness: str = "ready"  # ready, warnings, blocked
