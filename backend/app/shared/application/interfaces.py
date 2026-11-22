"""
Application Layer Interfaces & Repositories (ARC-03 §7.2 & §7.3).
Defines abstract contracts using Python Protocols for strict dependency inversion.
"""

import uuid
from typing import Protocol

from app.shared.domain.entities import MenuEntity


class MenuRepository(Protocol):
    """Abstract interface for Menu persistence operations."""

    async def get_by_id(self, menu_id: uuid.UUID) -> MenuEntity | None: ...

    async def get_by_slug(self, restaurant_id: uuid.UUID, slug: str) -> MenuEntity | None: ...

    async def list_for_restaurant(self, restaurant_id: uuid.UUID) -> list[MenuEntity]: ...

    async def add(self, menu: MenuEntity) -> MenuEntity: ...

    async def delete(self, menu_id: uuid.UUID) -> None: ...


class UnitOfWork(Protocol):
    """Abstract interface for controlling atomic transaction boundaries."""

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self): ...

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
