"""Unit of Work port defining atomic transaction boundary contracts (FCD-06 §11.2)."""

from typing import Protocol, Self

from menu_it.domain.ports.repositories import RestaurantProfileRepository


class MenuItUnitOfWork(Protocol):
    """Port defining atomic persistence transaction and repository coordinator."""

    restaurant_profiles: RestaurantProfileRepository

    async def __aenter__(self) -> Self:
        """Enter transactional context."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit transactional context with automatic rollback on unhandled error."""
        ...

    async def commit(self) -> None:
        """Commit current transaction atomically."""
        ...

    async def rollback(self) -> None:
        """Rollback current transaction."""
        ...
