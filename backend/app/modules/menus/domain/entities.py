"""
Menu Domain Entities (ARC-04 §6.4, MOD-04).
"""
from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class MenuStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class Menu:
    id: UUID
    restaurant_id: UUID
    name: str
    status: MenuStatus = MenuStatus.DRAFT

    def __post_init__(self) -> None:
        self.rename(self.name)

    def rename(self, name: str) -> None:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Menu name is required")
        if len(normalized) > 255:
            raise ValueError("Menu name cannot exceed 255 characters")
        self.name = normalized

    def activate(self) -> None:
        self.status = MenuStatus.ACTIVE

    def archive(self) -> None:
        self.status = MenuStatus.ARCHIVED
