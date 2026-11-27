"""Domain error primitives for business-rule violations (FCD-06 §6.1)."""


class DomainError(Exception):
    """Base class for all business-rule violations."""


class ValidationDomainError(DomainError):
    """Raised when a value or entity violates a domain business invariant."""


class EntityNotFoundError(DomainError):
    """Raised when the requested domain entity does not exist."""


class InvalidStateTransitionError(DomainError):
    """Raised when an entity lifecycle transition is not permitted."""


class BusinessRuleViolationError(DomainError):
    """Raised when an operation violates a domain business rule."""


class ConcurrencyConflictError(DomainError):
    """Raised when an entity changed while an operation was in progress."""
