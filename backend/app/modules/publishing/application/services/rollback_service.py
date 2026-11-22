"""
Publication Rollback Engine (ARC-10 §12, WP-ARC10-08).
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from app.modules.publishing.application.services.publication_service import PublicationService
from app.modules.publishing.domain.entities import ActivePublication, PublicationActivation
from app.modules.publishing.domain.events import PublicationEvent
from app.modules.publishing.domain.exceptions import (
    ActivePublicationConflictError,
    PublicationNotFoundError,
    RendererIncompatibleError,
    SnapshotIntegrityError,
)
from app.modules.publishing.domain.value_objects import (
    ActivationReason,
    PublicationStatus,
)


class RollbackService:
    """
    Executes non-destructive historical snapshot reactivation and audit logging.
    """

    def __init__(self, publication_service: PublicationService):
        self.pub_service = publication_service

    async def rollback(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        menu_id: UUID,
        target_publication_id: UUID,
        expected_active_publication_id: Optional[UUID] = None,
        actor_id: Optional[UUID] = None,
        reason: str = "Rollback to previous publication version",
    ) -> Dict[str, Any]:
        async with self.pub_service._get_menu_lock(menu_id):
            now = datetime.now(timezone.utc)
            current_active = self.pub_service.active_publications.get(menu_id)

            # 1. Expected active version verification (concurrency conflict prevention)
            if expected_active_publication_id is not None:
                current_active_id = current_active.publication_id if current_active else None
                if current_active_id != expected_active_publication_id:
                    raise ActivePublicationConflictError(
                        f"Current active publication {current_active_id} does not match expected {expected_active_publication_id}"
                    )

            # 2. Target publication exists and belongs to menu
            target_pub = self.pub_service.get_publication_by_id(menu_id, target_publication_id)
            if not target_pub:
                raise PublicationNotFoundError(f"Target publication {target_publication_id} not found for menu {menu_id}")

            if target_pub.organization_id != organization_id:
                raise PublicationNotFoundError("Target publication does not belong to the requested organization")

            # 3. Snapshot exists and check compatibility
            snapshot = self.pub_service.get_snapshot(target_pub.snapshot_id)
            if snapshot:
                # Check renderer compatibility
                if snapshot.payload.get("presentation", {}).get("renderer_contract_version") == "0.9":
                    raise RendererIncompatibleError("Target snapshot uses deprecated and unsupported renderer contract 0.9")
                self.pub_service.snapshot_builder.verify_integrity(snapshot)

            # 5. Atomically update active publication pointer (ARC-10 §12.1)
            prev_active_id = current_active.publication_id if current_active else None
            self.pub_service.active_publications[menu_id] = ActivePublication(
                organization_id=organization_id,
                menu_id=menu_id,
                publication_id=target_publication_id,
                updated_at=now,
            )

            # Update statuses
            for p in self.pub_service.publications.get(menu_id, []):
                if p.id == target_publication_id:
                    p.status = PublicationStatus.ACTIVE
                    p.activated_at = now
                    p.activation_reason = ActivationReason.ROLLBACK
                elif p.id == prev_active_id:
                    p.status = PublicationStatus.SUPERSEDED

            # 6. Record activation history (ARC-10 §8.4)
            operation_id = uuid4()
            activation_record = PublicationActivation(
                id=uuid4(),
                organization_id=organization_id,
                menu_id=menu_id,
                publication_id=target_publication_id,
                previous_publication_id=prev_active_id,
                operation_id=operation_id,
                activation_reason=ActivationReason.ROLLBACK,
                actor_id=actor_id,
                activated_at=now,
            )
            self.pub_service.activations.setdefault(menu_id, []).append(activation_record)

            # 7. Record outbox event MenuRolledBack (ARC-10 §13.2)
            outbox_event = PublicationEvent(
                id=uuid4(),
                organization_id=organization_id,
                aggregate_type="MenuPublication",
                aggregate_id=target_publication_id,
                event_type="MenuRolledBack",
                payload={
                    "publication_id": str(target_publication_id),
                    "menu_id": str(menu_id),
                    "restaurant_id": str(restaurant_id),
                    "previous_publication_id": str(prev_active_id) if prev_active_id else None,
                    "target_version_number": target_pub.version_number,
                    "reason": reason,
                },
                occurred_at=now,
            )
            self.pub_service.outbox_events.append(outbox_event)

            return {
                "operation_id": operation_id,
                "publication": target_pub,
                "active_publication_id": target_publication_id,
                "status": "rolled_back",
            }
