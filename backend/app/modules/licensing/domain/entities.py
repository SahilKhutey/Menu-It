"""
Subscription & Licensing Domain Entities (ARC-04 §6.15, MOD-15).
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


@dataclass
class License:
    license_id: UUID
    organization_id: UUID
    license_key: str
    entitled_features: set[str] = field(default_factory=set)
    expires_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_revoked: bool = False

    def is_valid(self) -> bool:
        if self.is_revoked:
            return False
        if datetime.now(UTC) > self.expires_at:
            return False
        # Basic signature/key check (valid keys start with "LIC-")
        if not self.license_key.startswith("LIC-") or len(self.license_key) < 16:
            return False
        return True

    def can_access_feature(self, feature_key: str) -> bool:
        if not self.is_valid():
            return False
        return feature_key in self.entitled_features
