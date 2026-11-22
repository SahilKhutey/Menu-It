"""
Publication Reconciliation Service (ARC-10 §25.4, WP-ARC10-14).
"""
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

from app.modules.publishing.application.services.publication_service import PublicationService
from app.modules.publishing.domain.value_objects import PublicationStatus


class ReconciliationService:
    """
    Performs integrity audits and safely reconciles inconsistent publishing states.
    """

    def __init__(self, publication_service: PublicationService):
        self.pub_service = publication_service

    def audit_menu_publications(self, menu_id: UUID) -> Dict[str, Any]:
        discrepancies: List[Dict[str, Any]] = []

        active_ptr = self.pub_service.active_publications.get(menu_id)
        pubs = self.pub_service.publications.get(menu_id, [])
        pub_map = {p.id: p for p in pubs}

        # 1. Active pointer references existing publication
        if active_ptr:
            if active_ptr.publication_id not in pub_map:
                discrepancies.append({
                    "type": "ORPHANED_ACTIVE_POINTER",
                    "detail": f"Active pointer references non-existent publication {active_ptr.publication_id}",
                    "severity": "CRITICAL",
                })
            else:
                active_pub = pub_map[active_ptr.publication_id]
                if active_pub.status != PublicationStatus.ACTIVE:
                    discrepancies.append({
                        "type": "ACTIVE_POINTER_STATUS_MISMATCH",
                        "detail": f"Publication {active_pub.id} is marked {active_pub.status} but is pointed to by active pointer",
                        "severity": "HIGH",
                    })

        # 2. Check snapshot existence and integrity
        for p in pubs:
            snapshot = self.pub_service.get_snapshot(p.snapshot_id)
            if not snapshot:
                discrepancies.append({
                    "type": "MISSING_SNAPSHOT",
                    "detail": f"Publication {p.id} references missing snapshot {p.snapshot_id}",
                    "severity": "CRITICAL",
                })
            else:
                try:
                    self.pub_service.snapshot_builder.verify_integrity(snapshot)
                except Exception as exc:
                    discrepancies.append({
                        "type": "CORRUPTED_SNAPSHOT_HASH",
                        "detail": f"Snapshot {p.snapshot_id} failed integrity verification: {exc}",
                        "severity": "CRITICAL",
                    })

        # 3. Check for duplicate versions
        version_counts: Dict[int, int] = {}
        for p in pubs:
            version_counts[p.version_number] = version_counts.get(p.version_number, 0) + 1
        for ver, count in version_counts.items():
            if count > 1:
                discrepancies.append({
                    "type": "DUPLICATE_VERSION_NUMBER",
                    "detail": f"Version number {ver} is assigned to {count} publications",
                    "severity": "CRITICAL",
                })

        return {
            "menu_id": menu_id,
            "discrepancies": discrepancies,
            "is_clean": len(discrepancies) == 0,
            "audited_at": datetime.now(timezone.utc),
        }

    def reconcile_active_pointer(self, menu_id: UUID) -> bool:
        """
        Idempotently fixes active publication status if pointed to by active pointer.
        Never rewrites historical snapshots or versions.
        """
        active_ptr = self.pub_service.active_publications.get(menu_id)
        if not active_ptr:
            return True

        pubs = self.pub_service.publications.get(menu_id, [])
        for p in pubs:
            if p.id == active_ptr.publication_id and p.status != PublicationStatus.ACTIVE:
                p.status = PublicationStatus.ACTIVE
                return True
        return False
