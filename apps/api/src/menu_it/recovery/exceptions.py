"""Password recovery domain exceptions (FCD-05 §11)."""


class RecoveryError(Exception):
    """Base exception for password recovery errors."""


class InvalidRecoveryTokenError(RecoveryError):
    """Raised when password reset token is unknown, expired, or consumed."""
