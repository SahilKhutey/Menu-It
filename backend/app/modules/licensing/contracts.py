"""
Public Contracts for Licensing Module (ARC-04 §8, MOD-15).
"""
from typing import Protocol
from uuid import UUID


class LicenseEvaluator(Protocol):
    def is_feature_entitled(self, organization_id: UUID, feature_key: str) -> bool:
        ...
