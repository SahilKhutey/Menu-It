"""Authentication domain exceptions (FCD-05 §7.3)."""


class AuthenticationError(Exception):
    """Base exception for authentication failures."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when email or password verification fails."""


class AccountNotActiveError(AuthenticationError):
    """Raised when account state prohibits authentication."""


class AccountLockedError(AccountNotActiveError):
    """Raised when an account is temporarily locked due to excessive failed attempts."""


class AccountSuspendedError(AccountNotActiveError):
    """Raised when an account has been administratively disabled."""


class AccountNotVerifiedError(AccountNotActiveError):
    """Raised when login policy requires verified email address."""
