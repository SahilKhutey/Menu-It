# Devlog 026 — FCD-12 Automated Testing & CI/CD Foundation

**Date:** 2026-11-26  
**Author:** AI Architecture & Core Engineering Team  
**Subject:** Implementation, Verification, and Release of FCD-12 Automated Testing & CI/CD Foundation  
**Milestone:** `v1.0.0-fcd12`  
**Phase:** Foundational Core Development (FCD-12)  
**Parent Documents:** FCD-01 through FCD-11, ARC-11 (Infrastructure & Deployment), ARC-12 (Security & Reliability)  

---

## 1. Objectives & Context

Phase **FCD-12** establishes the automated testing and continuous integration/continuous delivery (CI/CD) foundation across the Menu-It multi-tenant restaurant platform:
- Unified GitHub Actions workflow orchestrating repository verification, backend quality, frontend quality, PostgreSQL integration, and security scans.
- Backend testing infrastructure with custom markers, coverage measurement, and fast hermetic suites.
- Frontend testing infrastructure using Vitest, validating API client envelopes, error mapping, and theme engine resolvers.
- Database migration and PostgreSQL Row-Level Security (RLS) integration testing with ephemeral service containers.
- End-to-end browser testing with Playwright covering critical customer menu browsing, admin authentication, and tenant isolation flows.
- Multi-scanner security quality gates (Gitleaks, Bandit, pip-audit, pnpm audit).
- Reproducible multi-stage Docker builds (`menu-it-api`, `menu-it-web`, `menu-it-admin`) running as non-root users and tagged with Git commit SHAs and immutable digests.
- Multi-environment deployment workflows (Staging, Approval-gated Production, Release evidence archival).
- Post-deployment smoke testing verification (`tests/deployment/smoke.py`) and emergency rollback runbooks.
- 24 technical documents in `docs/development/FCD-12/`, 12 ADRs (`FCD12-ADR-001` through `FCD12-ADR-012`), and full verification of all 36 acceptance criteria (`AC-01` through `AC-36`).

---

## 2. Completed Work Packages & Deliverables

### WP-00 & WP-01: Baseline Audit & Testing Strategy
- Audited repository layout, package managers (pnpm v11, Python 3.12), test frameworks, and existing workflows.
- Defined testing pyramid spanning unit, component, integration, API contracts, E2E, performance, recovery, and production smoke tests.
- Published `00-repository-baseline-audit.md` and `01-testing-strategy.md`.

### WP-02: Backend Testing Infrastructure
- Configured custom Pytest markers (`unit`, `integration`, `api`, `security`, `database`, `tenant`, `slow`) and coverage XML reporting in `apps/api/pyproject.toml`.
- Verified 361 passing tests with zero regressions.
- Published `02-backend-testing.md`.

### WP-03: Frontend Testing Infrastructure
- Installed Vitest and configured `vitest.config.mjs` for workspace-wide test discovery.
- Added `"test": "vitest run"` scripts to `apps/web` and `apps/admin`.
- Added unit tests for Web API client, Admin API client, and Theme Engine deep merge resolver.
- Verified 3 passing test suites across workspace.
- Published `03-frontend-testing.md`.

### WP-04 & WP-05: Database Migrations & API Contract Testing
- Validated Alembic head revision `0008_security_audit_events`.
- Created PostgreSQL 16 container integration workflow in `.github/workflows/database-tests.yml`.
- Standardized API contract tests enforcing universal error envelopes and shared TypeScript types.
- Published `04-database-and-migration-testing.md` and `05-api-contract-testing.md`.

### WP-06 & WP-07: E2E Testing & Security Quality Gates
- Configured Playwright in `playwright.config.ts` and authored `tests/e2e/critical-flows.spec.ts`.
- Integrated automated security scans in `.github/workflows/security.yml` (Bandit, pip-audit, pnpm audit, secret detection).
- Published `06-e2e-testing.md` and `07-security-quality-gates.md`.

### WP-08 & WP-10: Performance Baselines & Supply Chain Hardening
- Created k6 performance smoke script in `tests/performance/api-smoke.js`.
- Enforced frozen lockfile installations and least-privilege workflow permissions (`permissions: contents: read`).
- Published `08-performance-and-reliability-testing.md` and `09-ci-security-and-supply-chain.md`.

### WP-11 & WP-12: Container Artifacts & Controlled Deployment
- Created multi-stage Dockerfiles:
  - `apps/api/Dockerfile` (FastAPI backend on port 8000, non-root `appuser`)
  - `apps/web/Dockerfile` (Next.js web frontend on port 3000, non-root `appuser`)
  - `apps/admin/Dockerfile` (Next.js admin frontend on port 3001, non-root `appuser`)
- Created container build workflow in `.github/workflows/build-images.yml`.
- Created deployment workflows in `deploy-staging.yml` and `deploy-production.yml` with approval gates.
- Published `10-artifact-and-container-strategy.md`.

### WP-13 to WP-17: Release Governance, Runbooks & Acceptance
- Enhanced `.github/PULL_REQUEST_TEMPLATE.md` with multi-tenancy, RLS, and security checklists.
- Created post-deployment smoke verification script `tests/deployment/smoke.py`.
- Formatted 12 Architecture Decision Records (`FCD12-ADR-001` through `FCD12-ADR-012`).
- Certified all 36 acceptance criteria `AC-01` through `AC-36`.

---

## 3. Verification & Quality Gates Summary

- **Backend Pytest Suite:** 361 tests passing (0 failures, 0 errors) in 41.57s.
- **Frontend Vitest Suite:** 3 test files passing (100% pass) across web, admin, and theme-engine.
- **Frontend Builds:** `pnpm --filter @menu-it/web build` and `pnpm --filter @menu-it/admin build` passing.
- **Ruff Linter & Formatter:** All checks passed across 367 files.
- **Prettier Code Style:** 100% matched files use Prettier style.
- **TypeScript Static Typing:** Zero errors across all 6 workspace packages.

---

## 4. Next Steps

With FCD-12 complete, Menu-It has established a production-grade automated delivery pipeline, reproducible container build infrastructure, and strict quality gates. The foundation is complete and ready for business feature delivery.
