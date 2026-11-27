"""Base domain primitives and error types (FCD-06 §6)."""

from menu_it.domain.base.aggregate import AggregateRoot
from menu_it.domain.base.domain_event import DomainEvent
from menu_it.domain.base.entity import Entity
from menu_it.domain.base.errors import (
    BusinessRuleViolationError,
    ConcurrencyConflictError,
    DomainError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    ValidationDomainError,
)

__all__ = [
    "AggregateRoot",
    "BusinessRuleViolationError",
    "ConcurrencyConflictError",
    "DomainError",
    "DomainEvent",
    "Entity",
    "EntityNotFoundError",
    "InvalidStateTransitionError",
    "ValidationDomainError",
]
