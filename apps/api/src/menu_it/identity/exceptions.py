"""Identity domain exceptions (FCD-05 §4.2)."""


class IdentityError(Exception):
    """Base exception for identity-related errors."""


class UserNotFoundError(IdentityError):
    """Raised when requested user account does not exist."""


class UserAlreadyExistsError(IdentityError):
    """Raised when registration email already exists."""


class InvalidAccountStatusError(IdentityError):
    """Raised when an account state prohibits the requested action."""
