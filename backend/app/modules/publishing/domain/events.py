"""
ARC-10 Domain Events for Publishing & Versioning.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID


@dataclass(frozen=True)
class PublicationEvent:
    id: UUID
    organization_id: UUID
    aggregate_type: str
    aggregate_id: UUID
    event_type: str
    payload: Dict[str, Any]
    occurred_at: datetime
    published_at: datetime | None = None
    attempts: int = 0
    last_error_code: str | None = None


@dataclass(frozen=True)
class MenuPublicationRequested:
    operation_id: UUID
    organization_id: UUID
    menu_id: UUID
    actor_id: UUID
    draft_revision: int
    occurred_at: datetime


@dataclass(frozen=True)
class MenuPublicationValidated:
    validation_id: UUID
    organization_id: UUID
    menu_id: UUID
    draft_revision: int
    occurred_at: datetime


@dataclass(frozen=True)
class MenuPublicationRejected:
    operation_id: UUID
    organization_id: UUID
    menu_id: UUID
    diagnostics: list[dict[str, Any]]
    occurred_at: datetime


@dataclass(frozen=True)
class MenuPublished:
    publication_id: UUID
    organization_id: UUID
    restaurant_id: UUID
    menu_id: UUID
    version_number: int
    snapshot_id: UUID
    snapshot_hash: str
    source_draft_revision: int
    actor_id: UUID
    occurred_at: datetime


@dataclass(frozen=True)
class MenuRolledBack:
    publication_id: UUID
    organization_id: UUID
    restaurant_id: UUID
    menu_id: UUID
    version_number: int
    previous_publication_id: UUID
    actor_id: UUID
    reason: str
    occurred_at: datetime


@dataclass(frozen=True)
class MenuPublicationScheduled:
    schedule_id: UUID
    organization_id: UUID
    menu_id: UUID
    draft_revision: int
    scheduled_at: datetime
    timezone_name: str
    actor_id: UUID
    occurred_at: datetime


@dataclass(frozen=True)
class MenuPublicationCancelled:
    schedule_id: UUID
    organization_id: UUID
    menu_id: UUID
    actor_id: UUID
    occurred_at: datetime


@dataclass(frozen=True)
class MenuPublicationFailed:
    operation_id: UUID
    organization_id: UUID
    menu_id: UUID
    error_code: str
    message: str
    occurred_at: datetime


@dataclass(frozen=True)
class MenuPublicationReconciled:
    operation_id: UUID
    organization_id: UUID
    menu_id: UUID
    resolution: str
    occurred_at: datetime
