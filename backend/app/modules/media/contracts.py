"""
Public Contracts for Media Management Module (ARC-04 §8, MOD-14).
"""
from typing import Protocol
from uuid import UUID


class MediaStorage(Protocol):
    def resolve_media_url(self, asset_id: UUID) -> str | None:
        ...
