"""
Publishing & Versioning Domain Entities (ARC-04 §6.13, MOD-13).
"""
from dataclasses import dataclass, field
import hashlib
import json
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class PublishedVersion:
    version_id: UUID
    publication_id: UUID
    version_number: int
    snapshot_payload: dict[str, Any]
    sha256_hash: str

    @classmethod
    def create(cls, version_id: UUID, publication_id: UUID, version_number: int, payload: dict[str, Any]) -> "PublishedVersion":
        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(serialized).hexdigest()
        return cls(
            version_id=version_id,
            publication_id=publication_id,
            version_number=version_number,
            snapshot_payload=payload,
            sha256_hash=digest,
        )


@dataclass
class Publication:
    publication_id: UUID
    menu_id: UUID
    active_version_id: UUID | None = None
    versions: list[PublishedVersion] = field(default_factory=list)

    def publish_version(self, version: PublishedVersion) -> None:
        if any(v.version_number == version.version_number for v in self.versions):
            raise ValueError(f"Version number {version.version_number} already published")
        self.versions.append(version)
        self.active_version_id = version.version_id

    def rollback_to_version(self, target_version_id: UUID) -> PublishedVersion:
        matching = [v for v in self.versions if v.version_id == target_version_id]
        if not matching:
            raise ValueError("Target version not found for rollback")
        target = matching[0]
        self.active_version_id = target.version_id
        return target
