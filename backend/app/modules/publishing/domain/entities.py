"""
Publishing & Versioning Domain Entities (ARC-04 §6.13, ARC-10 §4.1).
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.modules.publishing.domain.value_objects import (
    ActivationReason,
    OperationStatus,
    OperationType,
    PublicationStatus,
)


@dataclass(frozen=True)
class PublishedVersion:
    version_id: UUID
    publication_id: UUID
    version_number: int
    snapshot_payload: dict[str, Any]
    sha256_hash: str

    @classmethod
    def create(
        cls,
        version_id: UUID,
        publication_id: UUID,
        version_number: int,
        payload: dict[str, Any],
    ) -> "PublishedVersion":
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
    # ARC-10 extended fields with defaults for backward compatibility:
    id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    version_number: int = 1
    snapshot_id: Optional[UUID] = None
    snapshot_hash: str = ""
    source_draft_revision: int = 1
    status: PublicationStatus = PublicationStatus.ACTIVE
    created_by: Optional[UUID] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    activated_at: Optional[datetime] = None
    activation_reason: ActivationReason = ActivationReason.PUBLISH

    def __post_init__(self):
        if self.id is None:
            self.id = self.publication_id

    def publish_version(self, version: PublishedVersion) -> None:
        if any(v.version_number == version.version_number for v in self.versions):
            raise ValueError(f"Version number {version.version_number} already published")
        self.versions.append(version)
        self.active_version_id = version.version_id
        self.version_number = version.version_number
        self.snapshot_hash = version.sha256_hash

    def rollback_to_version(self, target_version_id: UUID) -> PublishedVersion:
        matching = [v for v in self.versions if v.version_id == target_version_id]
        if not matching:
            raise ValueError("Target version not found for rollback")
        target = matching[0]
        self.active_version_id = target.version_id
        self.version_number = target.version_number
        self.snapshot_hash = target.sha256_hash
        return target


@dataclass(frozen=True)
class DraftRevision:
    id: UUID
    organization_id: UUID
    menu_id: UUID
    revision_number: int
    payload: Dict[str, Any]
    content_hash: str
    parent_revision_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MenuDraft:
    id: UUID
    organization_id: UUID
    menu_id: UUID
    current_revision: int = 1
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class PublicationSnapshot:
    id: UUID
    organization_id: UUID
    menu_id: UUID
    schema_version: str
    payload: Dict[str, Any]
    content_hash: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ActivePublication:
    organization_id: UUID
    menu_id: UUID
    publication_id: UUID
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class PublicationActivation:
    id: UUID
    organization_id: UUID
    menu_id: UUID
    publication_id: UUID
    previous_publication_id: Optional[UUID]
    operation_id: UUID
    activation_reason: ActivationReason
    actor_id: Optional[UUID]
    activated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PublicationOperation:
    id: UUID
    organization_id: UUID
    menu_id: UUID
    actor_id: UUID
    operation_type: OperationType
    idempotency_key: str
    request_hash: str
    status: OperationStatus
    result_publication_id: Optional[UUID] = None
    error_code: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


@dataclass(frozen=True)
class PublicationValidationRecord:
    id: UUID
    organization_id: UUID
    menu_id: UUID
    draft_revision: int
    result: str
    diagnostics: List[Dict[str, Any]]
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ScheduledPublicationRecord:
    id: UUID
    organization_id: UUID
    menu_id: UUID
    draft_revision: int
    expected_active_publication_id: Optional[UUID]
    scheduled_at: datetime
    timezone_name: str
    status: str
    created_by: UUID
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class PublicationAuditRecord:
    id: UUID
    organization_id: UUID
    menu_id: UUID
    actor_id: Optional[UUID]
    action: str
    metadata: Dict[str, Any]
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
