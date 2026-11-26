# FCD-13 · Document 18 — Foundational Baseline Release Checklist

## 1. Objective
Provides the pre-flight verification checklist required before tagging and publishing the Menu-It `v0.1.0` Foundational Platform Baseline.

---

## 2. Pre-Flight Checklist

### 2.1 Code Quality & Static Analysis
- [x] All Python code passes Ruff linting (`python -m ruff check apps/api tests/deployment`).
- [x] All Python code passes Ruff formatting (`python -m ruff format --check apps/api tests/deployment`).
- [x] All TypeScript code passes Prettier style checks (`pnpm format:check`).
- [x] All 6 workspace packages pass TypeScript typecheck (`pnpm -r typecheck`).
- [x] Both Next.js apps pass ESLint checks (`pnpm -r lint`).

### 2.2 Test Coverage & Quality Gates
- [x] Complete backend test suite passes 100% (`385/385 passed`).
- [x] Dedicated FCD-13 integration test suite passes 100% (`24/24 passed`).
- [x] Architecture boundary AST test verifies zero infrastructure imports in domain.
- [x] Frontend unit test suites pass in `@menu-it/web`, `@menu-it/admin`, and `@menu-it/theme-engine`.
- [x] Post-deployment smoke probes pass (`tests/deployment/smoke.py`).

### 2.3 Database & Migrations
- [x] Alembic migration tree verified single-head (`0008_create_security_audit_events`).
- [x] Migrations apply cleanly to an empty PostgreSQL schema.
- [x] Multi-tenant Row-Level Security (RLS) constraints verified.

### 2.4 Artifacts & Documentation
- [x] Multi-stage Dockerfiles (`apps/api`, `apps/web`, `apps/admin`) execute as non-root.
- [x] Release notes authored in `release/RELEASE_NOTES.md`.
- [x] Release manifest authored in `release/RELEASE_MANIFEST.json`.
- [x] SHA256 checksums recorded in `release/CHECKSUMS.txt`.
- [x] Deployment reference documented in `release/DEPLOYMENT_REFERENCE.md`.
- [x] 24 comprehensive technical documents authored in `docs/development/FCD-13/`.
- [x] All 12 Architecture Decision Records (`FCD13-ADR-001` through `FCD13-ADR-012`) recorded.
- [x] All 42 Acceptance Criteria (`AC-01` through `AC-42`) certified.

---

## 3. Final Sign-Off
- **Release Engineer:** Menu-It Lead Systems Architect
- **Target Tag:** `v0.1.0`
- **Status:** **ALL CHECKS COMPLETE — APPROVED FOR RELEASE**
