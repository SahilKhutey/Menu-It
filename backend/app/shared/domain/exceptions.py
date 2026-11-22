"""
Domain Exception Hierarchy (ARC-03 §4.5 & §5).
Pure domain exceptions completely decoupled from HTTP frameworks.
"""


class DomainException(Exception):
    """Base exception for all domain rule violations."""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class EntityNotFoundException(DomainException):
    """Raised when an aggregate root or entity cannot be found."""

    def __init__(self, entity_name: str, identifier: str):
        super().__init__(
            f"{entity_name} with identifier '{identifier}' was not found.", code="ENTITY_NOT_FOUND"
        )


class BusinessRuleViolationException(DomainException):
    """Raised when an operation violates an explicit domain invariant."""

    def __init__(self, rule_name: str, message: str):
        super().__init__(f"Business rule '{rule_name}' violated: {message}", code="RULE_VIOLATION")


class InvariantViolationException(DomainException):
    """Raised when an immutable entity constraint is breached."""

    def __init__(self, message: str):
        super().__init__(message, code="INVARIANT_VIOLATION")
