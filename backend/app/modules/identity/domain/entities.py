"""
Identity Domain Entities (ARC-04 §6.1, MOD-01).
Pure Python models with authentication invariants.
"""

from dataclasses import dataclass
from uuid import UUID

from app.shared.domain.value_objects import EmailAddress


@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    is_active: bool = True
    is_verified: bool = False

    def __post_init__(self) -> None:
        # Validate email invariant
        normalized_email = EmailAddress(self.email).value
        self.email = normalized_email

    def deactivate(self) -> None:
        self.is_active = False

    def verify_email(self) -> None:
        self.is_verified = True

    def assert_can_authenticate(self) -> None:
        if not self.is_active:
            raise ValueError("Account is inactive and cannot authenticate")


@dataclass
class Session:
    id: UUID
    user_id: UUID
    is_revoked: bool = False

    def revoke(self) -> None:
        self.is_revoked = True

    def assert_valid(self) -> None:
        if self.is_revoked:
            raise ValueError("Session is revoked")
