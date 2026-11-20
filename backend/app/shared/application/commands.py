"""
Application Commands and Result DTOs (ARC-03 §5.2 & §5.3).
"""
from dataclasses import dataclass
from typing import Optional
import uuid


@dataclass(frozen=True)
class CreateMenuCommand:
    """Command payload for creating a new restaurant menu."""
    restaurant_id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    menu_type: str = "all_day"


@dataclass(frozen=True)
class MenuResult:
    """Application result DTO returned by menu use cases."""
    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    slug: str
    menu_type: str
    description: Optional[str]
