"""
Public Contracts for Publishing Module (ARC-04 §8, ARC-10 §10, MOD-13).
"""

from typing import Any, Protocol
from uuid import UUID


class PublishedSnapshotReader(Protocol):
    def get_active_snapshot(self, menu_id: UUID) -> dict[str, Any] | None: ...


class DraftRevisionReader(Protocol):
    def get_revision(self, menu_id: UUID, revision_number: int) -> dict[str, Any] | None: ...


class PublicationManagementService(Protocol):
    async def publish_menu(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        menu_id: UUID,
        draft_revision: int,
        candidate_payload: dict[str, Any],
        expected_active_publication_id: UUID | None = None,
        idempotency_key: str | None = None,
        actor_id: UUID | None = None,
        reason: str = "Publish menu update",
    ) -> dict[str, Any]: ...

    async def rollback(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        menu_id: UUID,
        target_publication_id: UUID,
        expected_active_publication_id: UUID | None = None,
        actor_id: UUID | None = None,
        reason: str = "Rollback",
    ) -> dict[str, Any]: ...
