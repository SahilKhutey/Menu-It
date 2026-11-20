"""
Rendering Domain Concepts (ARC-04 §6.11, MOD-11).
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RenderInput:
    published_snapshot: dict[str, Any]
    render_context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderResult:
    menu_data: dict[str, Any]
    theme: dict[str, Any]
    layout: dict[str, Any]
    components: list[dict[str, Any]]
