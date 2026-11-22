"""
Category Domain Entities (ARC-04 §6.5, MOD-05).
"""

from dataclasses import dataclass
from uuid import UUID

from app.shared.domain.value_objects import DisplayOrder


@dataclass
class Category:
    id: UUID
    menu_id: UUID
    name: str
    display_order: int = 0
    is_visible: bool = True

    def __post_init__(self) -> None:
        normalized = self.name.strip()
        if not normalized:
            raise ValueError("Category name is required")
        self.name = normalized
        # Validate non-negative display order
        self.display_order = DisplayOrder(self.display_order).value

    def reorder(self, new_order: int) -> None:
        self.display_order = DisplayOrder(new_order).value

    def hide(self) -> None:
        self.is_visible = False

    def unhide(self) -> None:
        self.is_visible = True
