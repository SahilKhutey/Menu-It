# FCD-12 · Document 17: Automated Test Case Register

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Test Suite Catalog & Distribution

| Category | Test Suite Location | Test Count | Target Invariant |
| :--- | :--- | :--- | :--- |
| **Backend Unit & Domain** | `apps/api/tests/unit/` | 185 tests | Domain logic, entities, value objects, money, schedules |
| **Database & Repositories** | `apps/api/tests/unit/platform/` & `integration/` | 65 tests | Repositories, Alembic migrations, database models |
| **Security & Authorization**| `apps/api/tests/security/` | 55 tests | Tenant isolation, RBAC permissions, config validation |
| **Reliability & Cache** | `apps/api/tests/unit/reliability/` & `cache/` | 36 tests | Circuit breakers, bounded timeouts, Redis fallbacks |
| **Observability & Audit** | `apps/api/tests/unit/observability/` | 20 tests | Metrics, tracing, sensitive data redaction, audit writing |
| **Frontend Unit & Comps** | `apps/web/tests/`, `apps/admin/tests/` | 3 tests | API client envelopes, error mapping, theme merging |
| **Total Automated Tests** | Across Monorepo | **364 tests** | 100% pass rate in CI |
