"""
Immutable Snapshot Builder & Integrity Engine (ARC-10 §7, WP-ARC10-05).
"""

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from app.modules.publishing.domain.entities import PublicationSnapshot
from app.modules.publishing.domain.exceptions import SnapshotIntegrityError
from app.modules.publishing.domain.services.canonical_hash import calculate_snapshot_hash

PUBLIC_ALLOWLIST_KEYS = {
    "restaurant": {
        "id",
        "name",
        "slug",
        "description",
        "logo_url",
        "cover_url",
        "display_name",
        "logo_reference",
        "public_contact_information",
    },
    "menu": {
        "id",
        "menu_id",
        "name",
        "title",
        "slug",
        "description",
        "menu_type",
        "locale",
        "currency",
        "visibility",
    },
    "categories": {
        "id",
        "category_id",
        "name",
        "title",
        "description",
        "image_url",
        "sort_order",
        "is_visible",
        "visibility",
        "items",
    },
    "items": {
        "id",
        "item_id",
        "name",
        "description",
        "base_price",
        "price",
        "currency_code",
        "dietary_type",
        "spice_level",
        "image_url",
        "ingredients",
        "allergens",
        "is_available",
        "is_featured",
        "sort_order",
        "variants",
    },
    "presentation": {
        "theme_id",
        "theme_version",
        "layout_id",
        "layout_version",
        "component_definitions",
        "component_instances",
        "tokens",
        "layout",
    },
}


class SnapshotBuilder:
    """
    Constructs normalized, schema-valid, dependency-pinned immutable snapshots.
    """

    def build_snapshot(
        self,
        *,
        organization_id: UUID,
        menu_id: UUID,
        candidate_payload: dict[str, Any],
        schema_version: str = "1.0",
        renderer_version: str = "1.0",
    ) -> PublicationSnapshot:
        # 1. Filter payload through strict public allowlist
        public_payload = self._apply_public_allowlist(candidate_payload)

        # 2. Pin rendering dependencies
        if "presentation" not in public_payload:
            public_payload["presentation"] = {}

        pres = public_payload["presentation"]
        pres.setdefault("theme_id", "modern_clean")
        pres.setdefault("theme_version", "1.0.0")
        pres.setdefault("layout_id", "category_first")
        pres.setdefault("layout_version", "1.0.0")
        pres["renderer_contract_version"] = renderer_version

        # 3. Calculate canonical deterministic hash
        content_hash = calculate_snapshot_hash(public_payload)

        snapshot_id = uuid4()
        return PublicationSnapshot(
            id=snapshot_id,
            organization_id=organization_id,
            menu_id=menu_id,
            schema_version=schema_version,
            payload=public_payload,
            content_hash=content_hash,
            created_at=datetime.now(UTC),
        )

    def verify_integrity(self, snapshot: PublicationSnapshot) -> bool:
        """Verifies that the snapshot content matches its cryptographic SHA-256 digest."""
        computed = calculate_snapshot_hash(snapshot.payload)
        if computed != snapshot.content_hash:
            raise SnapshotIntegrityError(
                f"Snapshot {snapshot.id} corrupted: expected {snapshot.content_hash}, got {computed}"
            )
        return True

    def _apply_public_allowlist(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Deep copy and filter to permitted public fields only."""
        clean: dict[str, Any] = {}

        # Restaurant section
        raw_rest = raw.get("restaurant", {})
        clean["restaurant"] = {
            k: v for k, v in raw_rest.items() if k in PUBLIC_ALLOWLIST_KEYS["restaurant"]
        }

        # Menu section
        raw_menu = raw.get("menu", {})
        clean["menu"] = {k: v for k, v in raw_menu.items() if k in PUBLIC_ALLOWLIST_KEYS["menu"]}

        # Categories & items
        raw_cats = raw.get("categories", [])
        clean_cats = []
        for cat in raw_cats:
            clean_cat = {k: v for k, v in cat.items() if k in PUBLIC_ALLOWLIST_KEYS["categories"]}
            clean_items = []
            for item in cat.get("items", []):
                clean_item = {k: v for k, v in item.items() if k in PUBLIC_ALLOWLIST_KEYS["items"]}
                clean_items.append(clean_item)
            clean_cat["items"] = clean_items
            clean_cats.append(clean_cat)
        clean["categories"] = clean_cats

        # Presentation section
        raw_pres = raw.get("presentation", {})
        clean["presentation"] = deepcopy(raw_pres)

        # Include theme/layout if at top level
        if "theme" in raw:
            clean["theme"] = deepcopy(raw["theme"])
        if "layout" in raw:
            clean["layout"] = deepcopy(raw["layout"])

        return clean
