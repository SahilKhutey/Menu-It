# 24 — Data Architecture Risk Register

## 1. Risk Register (ARC06-R01 – ARC06-R16)

| Risk ID | Risk Description | Severity | Mitigation | Status |
|---|---|---|---|---|
| ARC06-R01 | Missing tenant ownership column | Critical | Data ownership manifest | Mitigated |
| ARC06-R02 | Incorrect composite foreign keys | Critical | Composite constraints & tests | Mitigated |
| ARC06-R03 | RLS not applied to a new table | Critical | Manifest RLS coverage audit | Mitigated |
| ARC06-R04 | Runtime database role bypasses RLS | Critical | Restricted credentials (NOBYPASSRLS) | Mitigated |
| ARC06-R05 | Connection pool retains tenant context | Critical | Transaction-local settings | Mitigated |
| ARC06-R06 | Excessive JSONB use | High | Relational-first schema | Mitigated |
| ARC06-R07 | Mutable published snapshots | Critical | Immutability event guards & triggers | Mitigated |
| ARC06-R08 | Floating-point pricing | High | Integer minor units & Decimal | Mitigated |
| ARC06-R09 | Poor indexing | Medium | Composite indexes & EXPLAIN tests | Mitigated |
| ARC06-R10 | Destructive migrations | High | Expand-migrate-contract strategy | Mitigated |
| ARC06-R11 | Cascading deletion erasing audit data | High | Explicit lifecycle policies | Mitigated |
| ARC06-R12 | Database/media restore mismatch | High | Coordinated backup procedure | Mitigated |
| ARC06-R13 | Configuration schema drift | Medium | Versioned schemas & adapters | Mitigated |
| ARC06-R14 | Duplicate asynchronous events | Medium | Idempotent consumers & outbox | Mitigated |
| ARC06-R15 | Premature database partitioning | Low | Indexed relational tables baseline | Mitigated |
| ARC06-R16 | Unbounded query results | Medium | Server-enforced cursor limits | Mitigated |
