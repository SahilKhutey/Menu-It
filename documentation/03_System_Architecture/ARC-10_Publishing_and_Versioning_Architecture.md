# ARC-10 — Publishing & Versioning Architecture
**ModularMenu · System Architecture Series · Version 1.0**
**Proposed Architecture Baseline · Approved Engineering Specification**

---

## Document Control
| Attribute | Definition |
| :--- | :--- |
| **Document ID** | ARC-10 |
| **Title** | Publishing & Versioning Architecture |
| **Product** | ModularMenu |
| **Version** | 1.0 |
| **Status** | Approved Architectural Baseline |
| **Dependencies** | ARC-03, ARC-04, ARC-05, ARC-06, ARC-07, ARC-08, ARC-09 |
| **Downstream** | ARC-11 Infrastructure & Deployment Architecture |
| **Primary Technologies**| FastAPI, Python 3.12, PostgreSQL 16, SQLAlchemy 2.x, Next.js 14, TypeScript, JSON Schema, SHA-256 |

---

## 1. Executive Summary & Core Lifecycle
ARC-10 establishes how restaurant menu modifications transition from mutable working drafts into publicly accessible, immutable, versioned publications.

The publishing system forms the controlled boundary between the restaurant's operational configuration and its public digital menu:
1. **Draft Isolation:** A draft is never publicly accessible before explicit publication.
2. **Snapshot Immutability:** Every successful publication creates an immutable snapshot with a canonical SHA-256 digest.
3. **Atomic Activation:** Visitors see either the previous complete menu or the new complete menu; partial publications are physically prevented via database transactions.
4. **Autonomous Payload:** A publication snapshot packages all required category, item, variant, theme, and layout configurations.
5. **Auditable Traceability:** Every publish and rollback action is immutably recorded with actor, reason, and timestamp.
6. **Non-destructive Rollback:** Rollback activates an earlier valid snapshot without rewriting historical records or altering version sequences.
7. **Concurrency & Idempotency:** Optimistic revision locks (`If-Match`) and menu-level row locks prevent conflicting publishes; idempotency keys prevent duplicate activations.
8. **Public Delivery Alignment:** ARC-09 public renderer consumes strictly the active published snapshot via high-performance cached endpoints.

```
+---------------+     Validate Revision      +--------------------+
| Mutable Draft | ------------------------> | Validation Engine  |
+---------------+                            +--------------------+
                                                       | Passed
                                                       v
+-------------------+     Transactional      +--------------------+
| Public Activation | <-------------------- | Immutable Snapshot |
| (Active Pointer)  |        Commit         |   (SHA-256 Hash)   |
+-------------------+                        +--------------------+
          |
          v
+--------------------+
| ARC-09 Guest Menu  |
+--------------------+
```

---

## 2. Invariants & Guarantees
- **ARC10-I01 (Immutable publication):** Published snapshots are never modified or overwritten.
- **ARC10-I02 (Atomic activation):** Active pointer changes strictly within an ACID database transaction.
- **ARC10-I03 (Draft isolation):** Drafts cannot be resolved or served by public endpoints.
- **ARC10-I04 (Tenant isolation):** Every publication is scoped to a validated tenant organization and restaurant.
- **ARC10-I05 (Version identity):** Each publication has a monotonically increasing version integer per menu.
- **ARC10-I06 (Ordered history):** Version sequence is deterministic and non-gap within a menu.
- **ARC10-I07 (Auditable actions):** Every publication and rollback is traceable to an authenticated actor and operation ID.
- **ARC10-I08 (Optimistic concurrency):** Stale publication requests referencing an outdated draft revision are rejected with HTTP 409 Conflict.
- **ARC10-I09 (Exact dependencies):** Snapshots reference pinned theme, layout, and component versions.
- **ARC10-I10 (Renderer contract):** ARC-09 consumes approved public snapshot DTOs exclusively.
- **ARC10-I11 (Idempotency):** Retrying an identical operation with the same idempotency key returns the original result without creating duplicate versions.
- **ARC10-I12 (Cache correctness):** Cache invalidation ensures public visitors receive the current active publication within TTL limits.
- **ARC10-I13 (Recovery):** Interrupted workflows are reconciled idempotently without altering historical snapshots.
- **ARC10-I14 (Deployment portability):** Publishing logic executes identically in managed SaaS and self-hosted editions.
- **ARC10-I15 (Historical integrity):** Rollbacks create new activation events pointing to historical snapshots without modifying history.

---

## 3. Core Architecture & Work Packages
The architecture is structured across 15 standard work packages:
- **WP-ARC10-01:** Architecture & Contract Foundation (Schemas, manifests, generated types).
- **WP-ARC10-02:** Database & Persistence Foundation (PostgreSQL tables, constraints, RLS, triggers).
- **WP-ARC10-03:** Draft Revision Engine (Monotonic revisions, canonical hashing, optimistic locking).
- **WP-ARC10-04:** Publication Validation Engine (Rules, diagnostics, severity, revision binding).
- **WP-ARC10-05:** Snapshot Builder & Integrity Engine (Allowlist filtering, dependency pinning, canonical SHA-256).
- **WP-ARC10-06:** Publication Transaction & Activation (ACID commit, row locking, idempotency).
- **WP-ARC10-07:** Version History & Detail Queries (Deterministic ordering, pagination, snapshot inspection).
- **WP-ARC10-08:** Rollback Engine (Reactivating historical snapshots, compatibility verification).
- **WP-ARC10-09:** Event & Outbox Engine (Transactional outbox, worker claiming, at-least-once delivery).
- **WP-ARC10-10:** ARC-09 Renderer & Cache Integration (Active resolver, cache tags, ETag generation).
- **WP-ARC10-11:** Publishing API Implementation (REST endpoints, OpenAPI 3.1, TypeScript clients).
- **WP-ARC10-12:** Frontend Publishing Dashboard (Next.js features, readiness panel, history, rollback).
- **WP-ARC10-13:** Scheduling & Approval Foundation (P1 exact-revision schedules, approval bindings).
- **WP-ARC10-14:** Recovery, Observability & Operations (Reconciliation jobs, metrics, structured logs, runbooks).
- **WP-ARC10-15:** Final Integration, QA & Release (120-test catalogue, 100% pass rate, version tagging).

---

## 4. Architectural Verification & Acceptance Criteria
Verification requires 100% compliance across:
1. All 120 acceptance tests (`ARC10-T001` through `ARC10-T120`) passing.
2. Complete zero-regression pass rate for ARC-01 through ARC-09 test suites.
3. Successful Next.js frontend production build maintaining bundle budgets.
4. Complete 30-document architectural specification in `docs/architecture/ARC-10-publishing-versioning-architecture/`.
5. ADRs `ADR-0168` through `ADR-0191` documented in decision register.
