"""
Application Use Cases (ARC-03 §5.1 & §5.2).
Orchestrates domain entities, repositories, and transaction units of work.
"""

import uuid

from app.shared.application.commands import CreateMenuCommand, MenuResult
from app.shared.application.interfaces import MenuRepository, UnitOfWork
from app.shared.domain.entities import MenuEntity
from app.shared.domain.exceptions import BusinessRuleViolationException


class CreateMenuUseCase:
    """Use case coordinating Menu aggregate creation and atomic persistence."""

    def __init__(self, menu_repository: MenuRepository, unit_of_work: UnitOfWork):
        self.menu_repo = menu_repository
        self.uow = unit_of_work

    async def execute(self, command: CreateMenuCommand) -> MenuResult:
        # 1. Enforce uniqueness invariant within restaurant tenant scope
        existing = await self.menu_repo.get_by_slug(command.restaurant_id, command.slug)
        if existing:
            raise BusinessRuleViolationException(
                "DuplicateMenuSlug",
                f"A menu with slug '{command.slug}' already exists for this restaurant.",
            )

        # 2. Instantiate aggregate root (triggers domain invariant validations)
        menu_entity = MenuEntity(
            id=uuid.uuid4(),
            restaurant_id=command.restaurant_id,
            name=command.name,
            slug=command.slug,
            description=command.description,
            menu_type=command.menu_type,
            status="active",
        )

        # 3. Coordinate atomic transaction persistence
        async with self.uow:
            await self.menu_repo.add(menu_entity)
            await self.uow.commit()

        # 4. Map to application result DTO
        return MenuResult(
            id=menu_entity.id,
            restaurant_id=menu_entity.restaurant_id,
            name=menu_entity.name,
            slug=menu_entity.slug,
            menu_type=menu_entity.menu_type,
            description=menu_entity.description,
        )
