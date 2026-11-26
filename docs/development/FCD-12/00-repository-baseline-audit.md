# FCD-12 · Document 00: Repository and Pipeline Baseline Audit

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Executive Summary

Phase FCD-12 transforms the security, quality, multi-tenancy, and domain controls established across FCD-02 through FCD-11 into enforceable, automated CI/CD workflows. Prior to workflow construction, a comprehensive baseline audit of the repository toolchain, package managers, test suites, and workflows was performed.

### Audit Findings
1. **Repository Layout:** Modular monorepo with `apps/api` (FastAPI + SQLAlchemy async + Alembic), `apps/web` (Next.js 14), `apps/admin` (Next.js 14), and shared packages (`@menu-it/shared-types`, `@menu-it/design-tokens`, `@menu-it/theme-engine`, `@menu-it/ui`).
2. **Package Managers:** Python dependencies managed in `apps/api/pyproject.toml` (Python >=3.12); Node dependencies managed via `pnpm` (v11.11.0 / workspace protocol).
3. **Existing Workflows:** Early legacy workflows (`api-quality.yml`, `quality-gates.yml`) targeted outdated paths (`backend/`). New workflows created in `.github/workflows/` directly orchestrate `apps/api`, `apps/web`, `apps/admin`, and packages.
4. **Test Infrastructure:**
   - Backend: Pytest with 361 passing tests, SQLite for unit/security suites, and PostgreSQL for database migration/RLS integration suites.
   - Frontend: Vitest configured with `@testing-library`, verifying API client error envelopes, theme resolvers, and UI components.
5. **Quality Gates:** Ruff linter/formatter, Prettier (`pnpm format:check`), TypeScript type checking (`tsc --noEmit`), and ESLint (`pnpm -r lint`).

---

## 2. Toolchain Inventory

| Tool | Version | Role in Menu-It Pipeline |
| :--- | :--- | :--- |
| **Python** | 3.12.10 | Backend runtime and test execution |
| **Node.js** | 24.18.0 (LTS 20/22 compatible) | Frontend runtime and tooling |
| **pnpm** | 11.11.0 | Monorepo package management and lockfile enforcement |
| **Pytest** | 8.x / 9.x | Backend unit, integration, and security tests |
| **Ruff** | 0.16.x | Fast Python linting and code formatting |
| **Vitest** | 5.1.x | Frontend unit and component testing |
| **Alembic** | 1.13.x | PostgreSQL relational schema migrations |
| **Playwright** | 1.x | End-to-end browser workflow testing |
| **Docker** | Multi-stage | Reproducible container builds for API, Web, and Admin |
