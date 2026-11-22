"""
Publication Application Service (ARC-10 §10, WP-ARC10-06).
"""
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.modules.publishing.application.services.draft_revision_service import DraftRevisionService
from app.modules.publishing.application.services.publication_validator import PublicationValidator
from app.modules.publishing.application.services.snapshot_builder import SnapshotBuilder
from app.modules.publishing.domain.entities import (
    ActivePublication,
    Publication,
    PublicationActivation,
    PublicationOperation,
    PublicationSnapshot,
    PublishedVersion,
)
from app.modules.publishing.domain.events import MenuPublished, PublicationEvent
from app.modules.publishing.domain.exceptions import (
    ActivePublicationConflictError,
    DraftRevisionStaleError,
    IdempotencyKeyConflictError,
    PublicationDomainError,
    PublicationValidationError,
)
from app.modules.publishing.domain.services.canonical_hash import calculate_snapshot_hash
from app.modules.publishing.domain.value_objects import (
    ActivationReason,
    OperationStatus,
    OperationType,
    PublicationStatus,
)


class PublicationService:
    """
    Orchestrates atomic publication transactions, idempotency, version sequencing, and outbox event dispatch.
    """

    def __init__(
        self,
        draft_service: Optional[DraftRevisionService] = None,
        validator: Optional[PublicationValidator] = None,
        snapshot_builder: Optional[SnapshotBuilder] = None,
    ):
        self.draft_service = draft_service or DraftRevisionService()
        self.validator = validator or PublicationValidator()
        self.snapshot_builder = snapshot_builder or SnapshotBuilder()

        # In-memory stores for unit & domain testing
        self.publications: Dict[UUID, List[Publication]] = {}  # menu_id -> list of publications
        self.snapshots: Dict[UUID, PublicationSnapshot] = {}   # snapshot_id -> snapshot
        self.active_publications: Dict[UUID, ActivePublication] = {}  # menu_id -> active
        self.activations: Dict[UUID, List[PublicationActivation]] = {}  # menu_id -> list
        self.operations: Dict[str, PublicationOperation] = {}  # idempotency_key -> operation
        self.outbox_events: List[PublicationEvent] = []
        self._menu_locks: Dict[UUID, asyncio.Lock] = {}

    def _get_menu_lock(self, menu_id: UUID) -> asyncio.Lock:
        if menu_id not in self._menu_locks:
            self._menu_locks[menu_id] = asyncio.Lock()
        return self._menu_locks[menu_id]

    async def publish_menu(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        menu_id: UUID,
        draft_revision: int,
        candidate_payload: Dict[str, Any],
        expected_active_publication_id: Optional[UUID] = None,
        idempotency_key: Optional[str] = None,
        actor_id: Optional[UUID] = None,
        reason: str = "Publish menu update",
    ) -> Dict[str, Any]:
        req_hash = calculate_snapshot_hash(candidate_payload)
        operation_id = uuid4()
        now = datetime.now(timezone.utc)

        # 1. Idempotency Check (ARC-10 §11.1)
        if idempotency_key:
            scoped_key = f"{organization_id}:{menu_id}:{idempotency_key}"
            if scoped_key in self.operations:
                existing_op = self.operations[scoped_key]
                if existing_op.request_hash != req_hash:
                    raise IdempotencyKeyConflictError(
                        f"Idempotency key '{idempotency_key}' reused with conflicting request payload"
                    )
                # Return cached successful publication response
                active_pub = self.active_publications.get(menu_id)
                pub = self.get_publication_by_id(menu_id, existing_op.result_publication_id)
                return {
                    "operation_id": existing_op.id,
                    "publication": pub,
                    "active_publication_id": active_pub.publication_id if active_pub else pub.id,
                    "idempotent_replay": True,
                }

        # 2. Acquire menu publication lock (ARC-10 §11.2)
        async with self._get_menu_lock(menu_id):
            # 3. Optimistic active publication check
            current_active = self.active_publications.get(menu_id)
            if expected_active_publication_id is not None:
                current_active_id = current_active.publication_id if current_active else None
                if current_active_id != expected_active_publication_id:
                    raise ActivePublicationConflictError(
                        f"Active publication mismatch: expected {expected_active_publication_id}, got {current_active_id}"
                    )

            # 4. Validate publication readiness (ARC-10 §9)
            validation_report = self.validator.validate(
                menu_id=menu_id,
                draft_revision=draft_revision,
                candidate_payload=candidate_payload,
            )
            if validation_report.result == "FAILED":
                raise PublicationValidationError(
                    "Publication candidate failed validation rules",
                    diagnostics=[d.__dict__ for d in validation_report.errors],
                )

            # 5. Build immutable snapshot with public allowlist and SHA-256 (ARC-10 §7)
            snapshot = self.snapshot_builder.build_snapshot(
                organization_id=organization_id,
                menu_id=menu_id,
                candidate_payload=candidate_payload,
            )
            self.snapshots[snapshot.id] = snapshot

            # 6. Allocate monotonically increasing version number per menu (ARC-10 §4.4)
            menu_pubs = self.publications.setdefault(menu_id, [])
            next_version = (menu_pubs[-1].version_number + 1) if menu_pubs else 1

            # Mark any previously active publication as SUPERSEDED
            if current_active:
                for p in menu_pubs:
                    if p.id == current_active.publication_id:
                        p.status = PublicationStatus.SUPERSEDED

            # 7. Create Publication record
            publication_id = uuid4()
            pub_record = Publication(
                publication_id=publication_id,
                id=publication_id,
                organization_id=organization_id,
                menu_id=menu_id,
                version_number=next_version,
                snapshot_id=snapshot.id,
                snapshot_hash=snapshot.content_hash,
                source_draft_revision=draft_revision,
                status=PublicationStatus.ACTIVE,
                created_by=actor_id or uuid4(),
                created_at=now,
                activated_at=now,
                activation_reason=ActivationReason.PUBLISH,
                versions=[
                    PublishedVersion(
                        version_id=publication_id,
                        publication_id=publication_id,
                        version_number=next_version,
                        snapshot_payload=snapshot.payload,
                        sha256_hash=snapshot.content_hash,
                    )
                ],
            )
            menu_pubs.append(pub_record)

            # 8. Update Active Publication Pointer (ARC-10 §4.3)
            previous_pub_id = current_active.publication_id if current_active else None
            self.active_publications[menu_id] = ActivePublication(
                organization_id=organization_id,
                menu_id=menu_id,
                publication_id=publication_id,
                updated_at=now,
            )

            # 9. Record Activation History (ARC-10 §8.4)
            activation_record = PublicationActivation(
                id=uuid4(),
                organization_id=organization_id,
                menu_id=menu_id,
                publication_id=publication_id,
                previous_publication_id=previous_pub_id,
                operation_id=operation_id,
                activation_reason=ActivationReason.PUBLISH,
                actor_id=actor_id,
                activated_at=now,
            )
            self.activations.setdefault(menu_id, []).append(activation_record)

            # 10. Record Outbox Event (ARC-10 §13.2)
            outbox_event = PublicationEvent(
                id=uuid4(),
                organization_id=organization_id,
                aggregate_type="MenuPublication",
                aggregate_id=publication_id,
                event_type="MenuPublished",
                payload={
                    "publication_id": str(publication_id),
                    "menu_id": str(menu_id),
                    "restaurant_id": str(restaurant_id),
                    "version_number": next_version,
                    "snapshot_id": str(snapshot.id),
                    "snapshot_hash": snapshot.content_hash,
                },
                occurred_at=now,
            )
            self.outbox_events.append(outbox_event)

            # 11. Save Idempotency Operation Record (ARC-10 §11.1)
            if idempotency_key:
                op = PublicationOperation(
                    id=operation_id,
                    organization_id=organization_id,
                    menu_id=menu_id,
                    actor_id=actor_id or uuid4(),
                    operation_type=OperationType.PUBLISH,
                    idempotency_key=idempotency_key,
                    request_hash=req_hash,
                    status=OperationStatus.COMPLETED,
                    result_publication_id=publication_id,
                    created_at=now,
                    completed_at=now,
                )
                self.operations[f"{organization_id}:{menu_id}:{idempotency_key}"] = op

            return {
                "operation_id": operation_id,
                "publication": pub_record,
                "active_publication_id": publication_id,
                "idempotent_replay": False,
            }

    def get_active_publication(self, menu_id: UUID) -> Optional[Publication]:
        active_ptr = self.active_publications.get(menu_id)
        if not active_ptr:
            return None
        return self.get_publication_by_id(menu_id, active_ptr.publication_id)

    def get_publication_by_id(self, menu_id: UUID, pub_id: UUID) -> Optional[Publication]:
        for p in self.publications.get(menu_id, []):
            if p.id == pub_id or p.publication_id == pub_id:
                return p
        return None

    def list_publications(self, menu_id: UUID) -> List[Publication]:
        return sorted(self.publications.get(menu_id, []), key=lambda p: p.version_number, reverse=True)

    def get_snapshot(self, snapshot_id: UUID) -> Optional[PublicationSnapshot]:
        return self.snapshots.get(snapshot_id)
