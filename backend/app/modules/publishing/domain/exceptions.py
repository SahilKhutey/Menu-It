"""
ARC-10 Domain Exceptions for Publishing & Versioning.
"""


class PublicationDomainError(Exception):
    """Base domain exception for publishing module."""

    def __init__(self, message: str, code: str = "PUBLICATION_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class PublicationValidationError(PublicationDomainError):
    def __init__(self, message: str, diagnostics: list = None):
        super().__init__(message, code="PUBLICATION_VALIDATION_FAILED")
        self.diagnostics = diagnostics or []


class DraftRevisionStaleError(PublicationDomainError):
    def __init__(self, message: str = "Submitted draft revision is stale"):
        super().__init__(message, code="DRAFT_REVISION_STALE")


class ActivePublicationConflictError(PublicationDomainError):
    def __init__(self, message: str = "Active publication conflict detected"):
        super().__init__(message, code="ACTIVE_PUBLICATION_CONFLICT")


class IdempotencyKeyConflictError(PublicationDomainError):
    def __init__(self, message: str = "Idempotency key reused with different request payload"):
        super().__init__(message, code="IDEMPOTENCY_KEY_REUSED")


class PublicationNotFoundError(PublicationDomainError):
    def __init__(self, message: str = "Publication not found"):
        super().__init__(message, code="PUBLICATION_NOT_FOUND")


class SnapshotIntegrityError(PublicationDomainError):
    def __init__(self, message: str = "Snapshot integrity verification failed"):
        super().__init__(message, code="SNAPSHOT_INTEGRITY_FAILED")


class RendererIncompatibleError(PublicationDomainError):
    def __init__(self, message: str = "Snapshot incompatible with current renderer"):
        super().__init__(message, code="RENDERER_INCOMPATIBLE")


class ApprovalRequiredError(PublicationDomainError):
    def __init__(self, message: str = "Publication policy requires managerial approval"):
        super().__init__(message, code="APPROVAL_REQUIRED")


class PublicationOperationInProgressError(PublicationDomainError):
    def __init__(self, message: str = "A conflicting publication operation is in progress"):
        super().__init__(message, code="PUBLICATION_OPERATION_IN_PROGRESS")


class ScheduledPublicationExpiredError(PublicationDomainError):
    def __init__(self, message: str = "Scheduled publication window has expired"):
        super().__init__(message, code="SCHEDULED_PUBLICATION_EXPIRED")


class ImmutableRecordMutationError(PublicationDomainError):
    def __init__(self, message: str = "Immutable record cannot be modified or deleted"):
        super().__init__(message, code="IMMUTABLE_RECORD_MUTATION_FORBIDDEN")
