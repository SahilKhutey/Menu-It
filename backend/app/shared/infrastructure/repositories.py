"""
SQLAlchemy Infrastructure Repositories (ARC-03 §7.2 & §7.3).
Implements application layer interfaces using SQLAlchemy 2.0 Async.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.menus.models import Menu as MenuModel
from app.shared.application.interfaces import MenuRepository, UnitOfWork
from app.shared.domain.entities import MenuEntity


class SqlAlchemyMenuRepository(MenuRepository):
    """SQLAlchemy implementation of the MenuRepository contract."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, menu_id: uuid.UUID) -> MenuEntity | None:
        stmt = select(MenuModel).where(MenuModel.id == menu_id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_slug(self, restaurant_id: uuid.UUID, slug: str) -> MenuEntity | None:
        stmt = select(MenuModel).where(
            MenuModel.restaurant_id == restaurant_id, MenuModel.slug == slug
        )
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        if not model:
            return None
        return self._to_entity(model)

    async def list_for_restaurant(self, restaurant_id: uuid.UUID) -> list[MenuEntity]:
        stmt = (
            select(MenuModel)
            .where(MenuModel.restaurant_id == restaurant_id)
            .order_by(MenuModel.sort_order.asc(), MenuModel.created_at.asc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def add(self, entity: MenuEntity) -> MenuEntity:
        model = MenuModel(
            id=entity.id,
            restaurant_id=entity.restaurant_id,
            name=entity.name,
            slug=entity.slug,
            description=entity.description,
            menu_type=entity.menu_type,
            status=entity.status,
            sort_order=1,
        )
        self.session.add(model)
        return entity

    async def delete(self, menu_id: uuid.UUID) -> None:
        stmt = select(MenuModel).where(MenuModel.id == menu_id)
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self.session.delete(model)

    def _to_entity(self, model: MenuModel) -> MenuEntity:
        return MenuEntity(
            id=model.id,
            restaurant_id=model.restaurant_id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            menu_type=model.menu_type,
            status=model.status,
            created_at=model.created_at,
        )


class SqlAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy transaction coordinator managing atomic session boundaries."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
