# ARC-10 §3: Publishing Invariants & Guarantees
**Non-Negotiable System Invariants (ARC10-I01 - ARC10-I15)**

| ID | Invariant | Required Behavior |
| :--- | :--- | :--- |
| **ARC10-I01** | Immutable publication | Published snapshots are never modified or deleted. |
| **ARC10-I02** | Atomic activation | Active pointer changes transactionally in one ACID commit. |
| **ARC10-I03** | Draft isolation | Drafts cannot be resolved or served by public endpoints. |
| **ARC10-I04** | Tenant isolation | Every publication is scoped to a validated tenant organization and restaurant. |
| **ARC10-I05** | Version identity | Each publication has a unique monotonic version integer per menu. |
| **ARC10-I06** | Ordered history | Version sequence is deterministic and non-gap within a menu. |
| **ARC10-I07** | Auditable actions | Every publication and rollback is traceable to an authenticated actor and operation ID. |
| **ARC10-I08** | Optimistic concurrency | Stale publication requests referencing an outdated draft revision are rejected with HTTP 409 Conflict. |
| **ARC10-I09** | Exact dependencies | Snapshots reference pinned theme, layout, and component versions. |
| **ARC10-I10** | Renderer contract | ARC-09 consumes approved public snapshot DTOs exclusively. |
| **ARC10-I11** | Idempotency | Retrying an identical operation with the same idempotency key returns the original result without creating duplicate versions. |
| **ARC10-I12** | Cache correctness | Public cache cannot expose an incorrect active version beyond TTL limits. |
| **ARC10-I13** | Recovery | Interrupted workflows are reconciled idempotently without altering historical snapshots. |
| **ARC10-I14** | Deployment portability | Publishing business logic is identical in managed SaaS and self-hosted editions. |
| **ARC10-I15** | Historical integrity | Rollbacks create new activation events pointing to historical snapshots without modifying history. |
