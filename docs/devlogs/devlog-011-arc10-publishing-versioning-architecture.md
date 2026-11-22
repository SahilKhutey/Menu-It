# Devlog 011 — ARC-10 Publishing & Versioning Architecture

**Date:** 2026-11-22  
**Author:** AI Architecture Team  
**Subject:** Implementation, Verification, and Release of ARC-10 Publishing & Versioning Architecture  
**Release Tag:** `v1.0.0-arc10`  
**Parent Documents:** ARC-01 through ARC-09  

---

## 1. Objectives & Context
ARC-10 defines the controlled transition of restaurant menu changes from mutable working drafts into publicly accessible, immutable, versioned publications.
The release enforces:
- Complete draft isolation from public guests.
- Monotonic version numbering per menu (`v1`, `v2`, `v3`...).
- Cryptographically verified immutable snapshots via canonical SHA-256 hashing.
- Atomic publication activation within a single PostgreSQL ACID transaction.
- Non-destructive rollback restoring previous snapshots without rewriting history.
- Optimistic concurrency control via `If-Match` revision locking.
- Durable lifecycle event dispatch via the Transactional Outbox pattern.

---

## 2. Key Engineering Accomplishments
1. **Contract Foundation (`packages/contracts/`):**
   - Implemented 10 JSON Schemas (`draft-revision`, `publication-request`, `publication-response`, `publication-snapshot`, `publication-validation`, `publication-operation`, `publication-activation`, `rollback-request`, `publication-event`, `scheduled-publication`).
   - Generated TypeScript definitions in `packages/contracts/generated/publishing.ts` and exported via `src/index.ts`.
   - Packaged manifests (`publication-state-machine.json`, `publication-permissions.yaml`, etc.) and test fixtures.

2. **Publishing Domain & Application Services (`backend/app/modules/publishing/`):**
   - `DraftRevisionService`: Monotonic revisions, parent ancestry, and `If-Match` optimistic locking.
   - `PublicationValidator`: Multi-stage pre-flight verification across content, pricing, media, themes, layouts, and components with typed diagnostics.
   - `SnapshotBuilder`: Public allowlist filtering, dependency pinning, and canonical SHA-256 calculation.
   - `PublicationService`: Menu row locking, version allocation, active pointer updates, activation history logging, and outbox event recording.
   - `RollbackService`: Non-destructive historical snapshot reactivation with integrity and compatibility validation.
   - `OutboxProcessor`: Claiming worker with bounded exponential retries and dead-letter review.
   - `ReconciliationService`: Self-healing audit of active pointers, orphaned snapshots, and stuck outbox records.

3. **REST API Implementation (`backend/app/api/v1/publishing.py`):**
   - Canonical endpoints mounted: `/menus/{menu_id}/validate`, `/publication-readiness`, `/publish`, `/publications`, `/snapshot`, `/rollback`, `/active-publication`, `/publication-operations`, `/publication-schedules`, `/publication-audit`.
   - Updated OpenAPI 3.1 specifications (`openapi.json` and `openapi.yaml`).

4. **Frontend Dashboard Feature (`frontend/src/features/publishing/`):**
   - Implemented `ReadinessPanel`, `ValidationReportView`, `PublishDialog`, `VersionHistoryTable`, and `RollbackDialog`.
   - Created dashboard page `/app/menus/[menuId]/publishing`.
   - Next.js production build verified cleanly with **92 kB First Load JS** (< 120 kB ceiling).

5. **Automated Verification:**
   - 120/120 test scenarios passing in `tests/publishing/test_arc10_publishing_catalogue.py`.
   - 618/618 total platform tests passing with zero regressions across ARC-01 through ARC-10.

---

## 3. Decisions & Invariants Recorded
- Registered `ADR-0168` through `ADR-0191` in `docs/decisions/decision-register.md`.
- Enforced all 15 architecture invariants (`ARC10-I01` to `ARC10-I15`).
