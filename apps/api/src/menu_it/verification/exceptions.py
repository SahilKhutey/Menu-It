"""Email verification domain exceptions (FCD-05 §10)."""


class VerificationError(Exception):
    """Base exception for email verification errors."""


class InvalidVerificationTokenError(VerificationError):
    """Raised when an email verification token is unknown, expired, or consumed."""
