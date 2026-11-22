"""
Draft Revision Management Service (ARC-10 §6, WP-ARC10-03).
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from app.modules.publishing.domain.entities import DraftRevision, MenuDraft
from app.modules.publishing.domain.exceptions import (
    DraftRevisionStaleError,
    ImmutableRecordMutationError,
)
from app.modules.publishing.domain.services.canonical_hash import calculate_snapshot_hash


class DraftRevisionService:
    def __init__(self):
        # In-memory storage for repository / test harness decoupling
        self._drafts: dict[UUID, MenuDraft] = {}
        self._revisions: dict[UUID, list[DraftRevision]] = {}

    def get_or_create_draft(self, organization_id: UUID, menu_id: UUID) -> MenuDraft:
        if menu_id not in self._drafts:
            self._drafts[menu_id] = MenuDraft(
                id=uuid4(),
                organization_id=organization_id,
                menu_id=menu_id,
                current_revision=0,
            )
        return self._drafts[menu_id]

    def get_latest_revision(self, menu_id: UUID) -> DraftRevision | None:
        revs = self._revisions.get(menu_id, [])
        return revs[-1] if revs else None

    def get_revision(self, menu_id: UUID, revision_number: int) -> DraftRevision | None:
        revs = self._revisions.get(menu_id, [])
        for r in revs:
            if r.revision_number == revision_number:
                return r
        return None

    def list_revisions(self, menu_id: UUID) -> list[DraftRevision]:
        return list(self._revisions.get(menu_id, []))

    def save_revision(
        self,
        *,
        organization_id: UUID,
        menu_id: UUID,
        payload: dict[str, Any],
        expected_revision: int | None = None,
        created_by: UUID | None = None,
    ) -> DraftRevision:
        draft = self.get_or_create_draft(organization_id, menu_id)

        # Enforce optimistic concurrency (ARC-10 §6.2)
        if expected_revision is not None and expected_revision != draft.current_revision:
            raise DraftRevisionStaleError(
                f"Draft revision mismatch: expected {expected_revision}, current is {draft.current_revision}"
            )

        latest = self.get_latest_revision(menu_id)
        next_revision_number = draft.current_revision + 1
        content_hash = calculate_snapshot_hash(payload)

        new_rev = DraftRevision(
            id=uuid4(),
            organization_id=organization_id,
            menu_id=menu_id,
            revision_number=next_revision_number,
            payload=payload,
            content_hash=content_hash,
            parent_revision_id=latest.id if latest else None,
            created_by=created_by,
            created_at=datetime.now(UTC),
        )

        draft.current_revision = next_revision_number
        draft.updated_at = datetime.now(UTC)
        self._revisions.setdefault(menu_id, []).append(new_rev)
        return new_rev

    def mutate_saved_revision(self, revision_id: UUID) -> None:
        """Enforces ARC10-I01 & ARC10-I15 immutability check."""
        raise ImmutableRecordMutationError(
            "Saved draft revisions are strictly immutable and cannot be updated"
        )

    def delete_saved_revision(self, revision_id: UUID) -> None:
        """Enforces immutability: deletion forbidden."""
        raise ImmutableRecordMutationError("Saved draft revisions cannot be deleted")
