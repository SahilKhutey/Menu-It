"""
ARC-10 Domain Value Objects for Publishing & Versioning.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class PublicationStatus(StrEnum):
    READY = "READY"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    INACTIVE = "INACTIVE"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class OperationType(StrEnum):
    PUBLISH = "publish"
    ROLLBACK = "rollback"
    SCHEDULE = "schedule"
    RECONCILE = "reconcile"


class OperationStatus(StrEnum):
    REQUESTED = "REQUESTED"
    VALIDATING = "VALIDATING"
    PREPARING = "PREPARING"
    PREPARED = "PREPARED"
    ACTIVATING = "ACTIVATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class DiagnosticSeverity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ActivationReason(StrEnum):
    PUBLISH = "publish"
    ROLLBACK = "rollback"
    SCHEDULED = "scheduled"
    RECOVERY = "recovery"


@dataclass(frozen=True)
class Diagnostic:
    code: str
    path: str
    severity: DiagnosticSeverity
    message: str


@dataclass(frozen=True)
class ValidationReport:
    validation_id: UUID
    menu_id: UUID
    draft_revision: int
    result: str  # PASSED, FAILED, WARNING
    errors: tuple[Diagnostic, ...]
    warnings: tuple[Diagnostic, ...]
    validated_at: datetime
