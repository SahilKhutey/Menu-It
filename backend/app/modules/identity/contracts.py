"""
Public Contracts for Identity Module (ARC-04 §8, MOD-01).
"""

from typing import Protocol
from uuid import UUID


class IdentityVerifier(Protocol):
    def verify_user_active(self, user_id: UUID) -> bool: ...
