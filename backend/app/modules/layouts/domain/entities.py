"""
Layout Domain Entities (ARC-04 §6.9, MOD-09).
"""
from dataclasses import dataclass, field
from enum import Enum


class LayoutFamily(str, Enum):
    LIST = "list"
    GRID = "grid"
    HORIZONTAL_CARDS = "horizontal-cards"
    EDITORIAL = "editorial"


@dataclass
class LayoutDefinition:
    layout_id: str
    family: LayoutFamily
    supported_slots: list[str] = field(default_factory=lambda: ["header", "categories", "items", "footer"])
    schema_version: int = 1

    def __post_init__(self) -> None:
        if not self.layout_id or not self.layout_id.strip():
            raise ValueError("Layout ID is required")

    def validate_slot_compatibility(self, slot_name: str) -> bool:
        return slot_name in self.supported_slots
