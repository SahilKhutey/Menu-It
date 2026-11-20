"""
Unit tests for Application Layer and Domain Aggregate Behavior (ARC-03 §13 WP-ARC03-04 & §14.2).
Executes application use cases using test doubles without database or network dependencies.
"""
import uuid
import pytest
from app.shared.application.commands import CreateMenuCommand
from app.shared.application.use_cases import CreateMenuUseCase
from app.shared.domain.exceptions import BusinessRuleViolationException
from tests.fixtures.fakes import InMemoryMenuRepository, InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_app_001_create_menu_use_case_success():
    """
    APP-001 / BE-ARC03-004:
    Valid CreateMenuCommand successfully coordinates domain entity validation,
    in-memory persistence, and transaction commit.
    """
    repo = InMemoryMenuRepository()
    uow = InMemoryUnitOfWork()
    use_case = CreateMenuUseCase(menu_repository=repo, unit_of_work=uow)

    restaurant_id = uuid.uuid4()
    cmd = CreateMenuCommand(
        restaurant_id=restaurant_id,
        name="Artisanal Brunch",
        slug="artisanal-brunch",
        description="Fresh morning specialties",
        menu_type="brunch"
    )

    result = await use_case.execute(cmd)

    assert result.name == "Artisanal Brunch"
    assert result.slug == "artisanal-brunch"
    assert result.restaurant_id == restaurant_id
    assert uow.committed is True
    assert uow.rolled_back is False

    # Verify entity is stored in repository
    stored = await repo.get_by_id(result.id)
    assert stored is not None
    assert stored.name == "Artisanal Brunch"


@pytest.mark.asyncio
async def test_app_002_create_menu_with_invalid_slug_fails_domain_validation():
    """
    APP-002 / BE-ARC03-005:
    Submitting an invalid slug format (uppercase, spaces, special chars)
    triggers BusinessRuleViolationException before persistence.
    """
    repo = InMemoryMenuRepository()
    uow = InMemoryUnitOfWork()
    use_case = CreateMenuUseCase(menu_repository=repo, unit_of_work=uow)

    cmd = CreateMenuCommand(
        restaurant_id=uuid.uuid4(),
        name="Evening Dinner",
        slug="Evening_Dinner Invalid!",
    )

    with pytest.raises(BusinessRuleViolationException) as exc_info:
        await use_case.execute(cmd)

    assert "InvalidSlugFormat" in str(exc_info.value)
    assert uow.committed is False


@pytest.mark.asyncio
async def test_app_003_duplicate_slug_within_restaurant_rejected():
    """
    APP-003 / BE-ARC03-005:
    Creating two menus with identical slugs in the same restaurant is rejected.
    """
    repo = InMemoryMenuRepository()
    uow = InMemoryUnitOfWork()
    use_case = CreateMenuUseCase(menu_repository=repo, unit_of_work=uow)

    restaurant_id = uuid.uuid4()
    cmd1 = CreateMenuCommand(
        restaurant_id=restaurant_id,
        name="Lunch Tasting",
        slug="lunch-tasting"
    )
    await use_case.execute(cmd1)

    # Attempt second menu with duplicate slug
    cmd2 = CreateMenuCommand(
        restaurant_id=restaurant_id,
        name="Alternative Lunch",
        slug="lunch-tasting"
    )
    with pytest.raises(BusinessRuleViolationException) as exc_info:
        await use_case.execute(cmd2)

    assert "DuplicateMenuSlug" in str(exc_info.value)


@pytest.mark.asyncio
async def test_app_004_use_case_rolls_back_on_failure():
    """
    APP-004 / BE-ARC03-006:
    When an unexpected persistence failure occurs during execution,
    the Unit of Work automatically rolls back the transaction.
    """
    class FailingMenuRepository(InMemoryMenuRepository):
        async def add(self, menu):
            raise RuntimeError("Database disk failure simulated")

    repo = FailingMenuRepository()
    uow = InMemoryUnitOfWork()
    use_case = CreateMenuUseCase(menu_repository=repo, unit_of_work=uow)

    cmd = CreateMenuCommand(
        restaurant_id=uuid.uuid4(),
        name="Dinner",
        slug="dinner"
    )

    with pytest.raises(RuntimeError):
        await use_case.execute(cmd)

    assert uow.committed is False
    assert uow.rolled_back is True
