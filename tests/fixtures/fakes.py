"""
In-Memory Test Doubles & Fakes (ARC-03 §13 WP-ARC03-04 & §14.2 BE-ARC03-010).
Enables isolated domain and use-case testing without database drivers or network overhead.
"""
from typing import Dict, List, Optional
import uuid
from app.shared.application.interfaces import MenuRepository, UnitOfWork
from app.shared.domain.entities import MenuEntity


class InMemoryMenuRepository(MenuRepository):
    """Fake Menu Repository storing entities in a local Python dict."""
    def __init__(self):
        self._storage: Dict[uuid.UUID, MenuEntity] = {}

    async def get_by_id(self, menu_id: uuid.UUID) -> Optional[MenuEntity]:
        return self._storage.get(menu_id)

    async def get_by_slug(self, restaurant_id: uuid.UUID, slug: str) -> Optional[MenuEntity]:
        for entity in self._storage.values():
            if entity.restaurant_id == restaurant_id and entity.slug == slug:
                return entity
        return None

    async def list_for_restaurant(self, restaurant_id: uuid.UUID) -> List[MenuEntity]:
        return [e for e in self._storage.values() if e.restaurant_id == restaurant_id]

    async def add(self, menu: MenuEntity) -> MenuEntity:
        self._storage[menu.id] = menu
        return menu

    async def delete(self, menu_id: uuid.UUID) -> None:
        self._storage.pop(menu_id, None)


class InMemoryUnitOfWork(UnitOfWork):
    """Fake Unit of Work tracking commits and rollbacks without database dependencies."""
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
