"""
Food Item Domain Entities (ARC-04 §6.6, MOD-06).
"""
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID


class FoodItemStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEACTIVATED = "deactivated"


@dataclass
class FoodItem:
    id: UUID
    category_id: UUID
    name: str
    description: str = ""
    status: FoodItemStatus = FoodItemStatus.AVAILABLE
    dietary_labels: list[str] = field(default_factory=list)
    allergens: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        normalized = self.name.strip()
        if not normalized:
            raise ValueError("Food item name is required")
        self.name = normalized

    def deactivate(self) -> None:
        self.status = FoodItemStatus.DEACTIVATED

    def mark_unavailable(self) -> None:
        self.status = FoodItemStatus.UNAVAILABLE

    def mark_available(self) -> None:
        self.status = FoodItemStatus.AVAILABLE

    def assign_to_category(self, new_category_id: UUID) -> None:
        if not new_category_id:
            raise ValueError("Invalid category assignment")
        self.category_id = new_category_id
