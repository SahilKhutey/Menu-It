# FCD-13 · Document 15 — Integration Test Plan

## 1. Objective & Scope
This document details the multi-tiered test strategy, execution order, and verification criteria used to validate the Menu-It foundation across all integrated boundaries.

---

## 2. Test Execution Levels

| Level | Focus Area | Framework | Target Scope |
| :--- | :--- | :--- | :--- |
| **Level 1: Unit Tests** | Pure business logic, value objects | `pytest` / `vitest` | Domain value objects, UI tokens, math utilities |
| **Level 2: Architecture** | Dependency boundaries & Clean Architecture | `pytest` + `ast` | Domain independence, presentation decoupling |
| **Level 3: Component** | Services, lifecycle, template rendering | `pytest` | Lifecycle hooks, Jinja2 autoescaping, cache |
| **Level 4: Security** | Authentication, tenant isolation, RLS | `pytest` | TenantContext, contextvar, cross-tenant denial |
| **Level 5: Contracts** | API schema, response envelope, headers | `pytest` / `httpx` | OpenAPI 3.x, X-Request-ID, error envelope |
| **Level 6: End-to-End** | Full browser platform journeys | `playwright` | Public web routes, admin portal route protection |
| **Level 7: Deployment** | Live HTTP probe verification | `httpx` async | Health, database probe, system info, metrics |

---

## 3. Master Test Execution Sequence

1. **Static Quality & Formatting:**
   `python -m ruff check apps/api tests/deployment`
   `python -m ruff format --check apps/api tests/deployment`
   `pnpm format:check`
2. **Frontend Typecheck & Unit Tests:**
   `pnpm -r typecheck`
   `pnpm -r lint`
   `pnpm test`
3. **Backend & Architecture Tests:**
   `python -m pytest apps/api/tests -q`
4. **Post-Deployment Smoke Verification:**
   `python tests/deployment/smoke.py --in-process`
5. **E2E Browser Journeys:**
   `pnpm exec playwright test`

---

## 4. Acceptance Thresholds
- **Backend Pass Rate:** 100% (Zero test failures permitted).
- **Frontend Pass Rate:** 100% across all packages.
- **Flakiness Policy:** Retries are forbidden on core integration tests; tests must execute deterministically.
