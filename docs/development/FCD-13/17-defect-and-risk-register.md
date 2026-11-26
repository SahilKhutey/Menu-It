# FCD-13 · Document 17 — Defect & Risk Register

## 1. Objective
Records all identified defects, technical debts, operational risks, and their corresponding mitigations or resolutions across the foundational baseline release (`v0.1.0`).

---

## 2. Defect Resolution Summary

| Defect ID | Description | Severity | Resolution Implemented | Status |
| :--- | :--- | :---: | :--- | :---: |
| `DEF-001` | Non-UUID `X-Request-ID` headers caused potential trace formatting inconsistencies. | Low | Middleware sanitizes incoming header; invalid UUID strings are replaced with server-generated UUIDv4. | **RESOLVED** |
| `DEF-002` | `smoke.py` failed when executed outside `apps/api` due to missing `sys.path`. | Medium | Auto-resolves `apps/api/src` into `sys.path` dynamically when `--in-process` flag is set. | **RESOLVED** |
| `DEF-003` | `Money` addition operand `+` threw TypeError when applied directly. | Low | Refactored tests to use explicit `add(other)` and `multiply(factor)` domain methods. | **RESOLVED** |
| `DEF-004` | Audit event contract required explicit `event_id`, `event_type`, and `occurred_at`. | Medium | Aligned integration test constructors with authoritative `AuditEvent` dataclass fields. | **RESOLVED** |

---

## 3. Operational Risk Assessment

| Risk ID | Risk Description | Likelihood | Impact | Mitigation Strategy |
| :--- | :--- | :---: | :---: | :--- |
| `RSK-01` | Database connection exhaustion under heavy burst load. | Low | High | Connection pooling governed by `DATABASE_POOL_SIZE` (default 5, configurable) with timeout limits. |
| `RSK-02` | Redis connection failure during API request. | Medium | Low | `PlatformServices` container implements fallback to `InMemoryCacheBackend` and `InMemoryRateLimiter`. |
| `RSK-03` | Database migration failure during production deployment. | Low | High | Single-head Alembic validation in CI; migration execution precedes container swap; rollback runbook documented. |
| `RSK-04` | Accidental hardcoding of secrets in frontend bundles. | Low | Critical | Environment variables restricted to `NEXT_PUBLIC_` prefix; Next.js builds omit private server secrets. |
