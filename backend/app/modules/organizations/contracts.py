"""
Public Contracts for Organization Module (ARC-04 §8, MOD-02).
"""
from typing import Protocol
from uuid import UUID


class OrganizationReader(Protocol):
    def organization_exists(self, organization_id: UUID) -> bool:
        ...

    def is_user_member(self, organization_id: UUID, user_id: UUID) -> bool:
        ...
