"""Entity domain primitive establishing stable identity equality (FCD-06 §6.2)."""

from dataclasses import dataclass
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


@dataclass(eq=False)
class Entity(Generic[T]):
    """Domain object defined by a unique and immutable identity.

    Two entities of the same type with the same identifier are equal,
    regardless of whether their mutable business attributes differ.
    """

    id: UUID

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))
