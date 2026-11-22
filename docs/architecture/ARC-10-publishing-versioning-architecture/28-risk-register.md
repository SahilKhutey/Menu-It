# ARC-10 §28: Risk Register & Mitigations
**20 Architectural Risks and Safeguards**

1. **Draft accidentally exposed publicly:** Mitigated by strict separation of active publication pointer and public resolver.
2. **Partial publication in failure:** Mitigated by single PostgreSQL ACID transaction boundary.
3. **Concurrent version collision:** Mitigated by database row locks and unique monotonic version constraints.
4. **Stale draft publication:** Mitigated by optimistic concurrency `If-Match` revision checks.
5. **Snapshot modified after publication:** Mitigated by database immutability triggers and read-only runtime credentials.
6. **Private data copied into public snapshot:** Mitigated by strict public allowlist filtering.
7. **Incorrect rollback:** Mitigated by target snapshot integrity verification and renderer contract compatibility check.
8. **Lost publication event:** Mitigated by transactional outbox pattern.
9. **Duplicate event side effects:** Mitigated by idempotent consumer handlers.
10. **Stale public cache:** Mitigated by version-addressed cache keys and edge cache tag purges.
11. **Cross-tenant publication:** Mitigated by tenant-aware composite foreign keys and PostgreSQL RLS.
12. **Unsupported component in old snapshot:** Mitigated by pinned dependency compatibility matrix.
13. **Missing historical media:** Mitigated by asset retention policies and soft-deletion protection.
14. **Stuck scheduled publication:** Mitigated by automated reconciliation job and monitoring alerts.
15. **Approval on changed draft:** Mitigated by binding approvals strictly to revision numbers and content hashes.
16. **Database migration breaks history:** Mitigated by forward-only migration review and test automation.
17. **Excessive version storage:** Mitigated by structured JSONB storage and historical archival policies.
18. **Operational repair alters history:** Mitigated by immutable audit records and non-destructive reconciliation rules.
19. **Event worker backlog:** Mitigated by concurrent worker claiming (`FOR UPDATE SKIP LOCKED`) and metrics alerts.
20. **Self-hosted version divergence:** Mitigated by unified Python codebase shared across SaaS and customer-hosted editions.
