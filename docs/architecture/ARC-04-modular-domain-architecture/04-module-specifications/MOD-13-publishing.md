# MOD-13 — Publishing & Versioning Module Specification

**Module ID:** MOD-13  
**Tier:** Delivery and Publication (P0)  
**Package:** `app.modules.publishing`  

---

## 1. Ownership & Boundaries
- **Owns:** Publication lifecycle, version numbers, immutable snapshot generation, history, rollback.
- **Does Not Own:** Menu editing drafts, dish recipes, billing calculations.

## 2. Domain Model & Invariants
- **PublishedVersion Value Object:** `PublishedVersion(version_id, publication_id, version_number, snapshot_payload, sha256_hash)`
  - Frozen, write-once snapshot stamped with SHA-256 digest.
- **Publication Aggregate:** `Publication(publication_id, menu_id, active_version_id, versions)`
  - Reversible rollback to existing version via `rollback_to_version()`.

## 3. Public Contracts & Events
- **Provides:** `PublishedSnapshotReader` Protocol (`get_active_snapshot`).
- **Consumes:** `MenuReader`, `CategoryReader`, `FoodItemReader`, `PricingReader`, `ThemeResolver`, `LayoutResolver`, `ComponentRegistryReader`.
- **Emits:** `MenuPublished` (EVT-014), `PublicationRolledBack` (EVT-015).
