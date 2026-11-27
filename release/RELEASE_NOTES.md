# Menu-It v0.1.0 — Foundational Platform Baseline Release Notes

## Release Summary

Menu-It `v0.1.0` marks the successful completion of the Foundation & Core Development milestone (FCD-01 through FCD-13). It establishes the unified, multi-tenant modular monolith baseline platform upon which all subsequent restaurant SaaS business capabilities (menus, ordering, payments, reservations, kitchen display, and analytics) will be developed.

The foundational release unifies the backend REST API (`apps/api`), customer-facing web application (`apps/web`), platform administrative dashboard (`apps/admin`), design tokens, and shared TypeScript contracts under a verified Clean Architecture and security boundary.

---

## Included Foundations (FCD-01 to FCD-12)

1. **FCD-01 — Repository & Monorepo Setup:** pnpm workspace, Python 3.12, TypeScript 5.4, strict linting and formatting.
2. **FCD-02 — Application Foundation:** FastAPI application factory, `/api/v1` versioning, request IDs, universal response envelopes.
3. **FCD-03 — Database Foundation:** PostgreSQL 16, async SQLAlchemy 2.x, Alembic single-head migrations (0001–0008), repository pattern.
4. **FCD-04 — Multi-Tenant Core:** Immutable `TenantContext`, PostgreSQL Row-Level Security (RLS), connection-pool tenant isolation.
5. **FCD-05 — Identity & Authorization:** JWT authentication, argon2 password hashing, organization membership resolution, RBAC.
6. **FCD-06 — Domain Foundation:** Value objects (`Money`, `Address`, `Contact`, `TimeZone`, `OperatingHours`), domain events, aggregate roots.
7. **FCD-07 — API Infrastructure:** Idempotency keys, rate limiting, error envelope handling, CORS, OpenAPI 3.x generation.
8. **FCD-08 — Frontend Foundation:** Next.js 14 App Router, Tailwind CSS design tokens, shared UI components (`@menu-it/ui`, `@menu-it/theme-engine`).
9. **FCD-09 — Core Platform Services:** `LocalFileStorage`, `NotificationService` (Jinja2 templates), logging, clock abstraction.
10. **FCD-10 — Caching, Background Jobs & Events:** Redis caching, ARQ worker registry, Transactional Outbox pattern (`event_outbox`).
11. **FCD-11 — Security, Reliability & Observability:** Prometheus metrics (`/api/v1/metrics`), structured JSON logging, security audit events, circuit breaker.
12. **FCD-12 — Automated Testing & CI/CD:** GitHub Actions workflows (CI orchestrator, tests, security, Docker builds, deployments), Vitest, Playwright E2E, deployment smoke tests.

---

## Verification & Quality Gate Metrics

- **Backend Quality:** 385 automated tests passing (100% green: unit, contract, security, database, and integration).
- **Frontend Quality:** 3 test suites passing across `@menu-it/web`, `@menu-it/admin`, and packages.
- **Architecture Boundaries:** AST-based automated import checker verifies pure domain layer with zero infrastructure coupling.
- **Tenant Isolation:** Verified PostgreSQL RLS enforcement, cross-tenant access denial, and background worker tenant context propagation.
- **Deployment Smoke Probes:** 4/4 passing in-process and against staging environments (`health`, `database`, `system/info`, `metrics`).
- **Static Analysis & Typecheck:** 100% compliant across Ruff, Prettier, TypeScript `tsc --noEmit`, and ESLint.

---

## Known Limitations & Deferred Capabilities

- Business domains (Menu builder, live order processing, payment gateways, KDS, inventory tracking) are deferred to subsequent business phases (starting with FCD-14: Organization & Restaurant Management).
- External cloud storage (AWS S3) and cloud email (SendGrid/SES) adapters are implemented as pluggable ports; local disk storage and console email adapters are default in v0.1.0.

---

## Deployment & Migration Reference

- Database migration sequence: `alembic upgrade head` applies revisions 0001 through 0008 sequentially before starting API containers.
- Container images: Non-root execution (`appuser:appuser` / `nextjs:nodejs`), immutable SHA256 digests.
- See [DEPLOYMENT_REFERENCE.md](file:///c:/Users/ASUS/Documents/Menu-it/release/DEPLOYMENT_REFERENCE.md) for full configuration directives.

---

## Rollback Procedure

If post-deployment smoke tests or health probes fail:

1. Re-route traffic to previous healthy container deployment via reverse proxy / load balancer.
2. In the event of schema rollback requirements, execute `alembic downgrade -1` or restore from verified PostgreSQL dump.
3. See [docs/development/FCD-13/19-rollback-and-recovery-report.md](file:///c:/Users/ASUS/Documents/Menu-it/docs/development/FCD-13/19-rollback-and-recovery-report.md) for step-by-step runbook.

---

## Release Identity

- **Version:** `v0.1.0`
- **Release Name:** Menu-It Foundational Platform Baseline
- **Milestone:** FCD-13 (P0 Foundation Completion)
- **Target Branch:** `develop` / `main`
