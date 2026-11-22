"""
Component Registry Domain Entities (ARC-04 §6.10, MOD-10).
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ComponentDefinition:
    component_id: str
    version: int
    schema: dict[str, Any] = field(default_factory=dict)
    supported_layouts: tuple[str, ...] = ("list", "grid", "horizontal-cards", "editorial")
    enabled: bool = True
    is_deprecated: bool = False

    def __post_init__(self) -> None:
        if not self.component_id or not self.component_id.strip():
            raise ValueError("Component ID cannot be empty")
        if self.version < 1:
            raise ValueError("Component version must be a positive integer")

    def supports_layout(self, layout_id: str) -> bool:
        return layout_id in self.supported_layouts

    def validate_properties(self, properties: dict[str, Any]) -> None:
        """Validate component properties against allowed schema properties."""
        allowed_props = self.schema.get("properties", {})
        for prop in properties:
            if prop not in allowed_props:
                raise ValueError(
                    f"Property '{prop}' is not supported by component '{self.component_id}'"
                )
