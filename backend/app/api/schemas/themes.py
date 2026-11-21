"""
ModularMenu — Themes, Layouts & Components API Schemas (ARC-07 §4.6).
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ThemeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    is_system_preset: bool
    tokens: Dict[str, Any]
    created_at: datetime


class LayoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    supported_slots: List[str]
    is_system_preset: bool


class ComponentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    component_key: str
    name: str
    category: str
    props_schema: Dict[str, Any]
    is_deprecated: bool = False
