"""
Application Layer Interfaces & Repositories (ARC-03 §7.2 & §7.3).
Defines abstract contracts using Python Protocols for strict dependency inversion.
"""
from typing import List, Optional, Protocol
import uuid
from app.shared.domain.entities import MenuEntity


class MenuRepository(Protocol):
    """Abstract interface for Menu persistence operations."""
    async def get_by_id(self, menu_id: uuid.UUID) -> Optional[MenuEntity]:
        ...

    async def get_by_slug(self, restaurant_id: uuid.UUID, slug: str) -> Optional[MenuEntity]:
        ...

    async def list_for_restaurant(self, restaurant_id: uuid.UUID) -> List[MenuEntity]:
        ...

    async def add(self, menu: MenuEntity) -> MenuEntity:
        ...

    async def delete(self, menu_id: uuid.UUID) -> None:
        ...


class UnitOfWork(Protocol):
    """Abstract interface for controlling atomic transaction boundaries."""
    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...
