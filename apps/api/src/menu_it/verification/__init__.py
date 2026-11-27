"""Email verification package initialization (FCD-05 §10)."""

from menu_it.verification.exceptions import (
    InvalidVerificationTokenError,
    VerificationError,
)
from menu_it.verification.service import EmailVerificationService

__all__ = [
    "EmailVerificationService",
    "InvalidVerificationTokenError",
    "VerificationError",
]
