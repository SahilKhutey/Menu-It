# ModularMenu Developer Log (Devlog) Index

Welcome to the official developer log archive for **ModularMenu** (Menu-It).
This directory contains chronological engineering chronicles capturing the architecture, implementation, design challenges, benchmark results, and release notes across all milestones.

---

## 📅 Chronological Log Registry

| ID | Title | Date | Milestone / Tag | Key Highlights |
| :--- | :--- | :--- | :--- | :--- |
| **[Devlog-001](devlog-001-project-initialization-and-blueprint.md)** | **Project Initialization & Blueprint Baseline** | 2026-11-19 | Pre-Alpha | Product vision, India-First, Web-First, hybrid hosting model, zero-fork invariant, commercial license. |
| **[Devlog-002](devlog-002-arc01-system-architecture-overview.md)** | **ARC-01 System Architecture Overview** | 2026-11-19 | `v1.0.0-arc01` | System boundaries, 7 external actors, 7 architectural layers, 10 non-negotiable invariants. |
| **[Devlog-003](devlog-003-arc02-architectural-principles-and-standards.md)** | **ARC-02 Architectural Principles & Standards** | 2026-11-19 | `v1.0.0-arc02` | 10 principles (P-01 to P-10), 16 constraints (CON-01 to CON-16), RFC 7807 error format, initial 23-test suite. |
| **[Devlog-004](devlog-004-arc03-application-architecture.md)** | **ARC-03 Application Architecture Baseline** | 2026-11-20 | `v1.0.0-arc03` | Modular monolith (Next.js 14 + FastAPI), layered backend, Repository & UoW protocols, 95.2 kB JS budget, 46 tests. |
| **[Devlog-005](devlog-005-arc04-modular-domain-architecture.md)** | **ARC-04 Modular Domain Architecture** | 2026-11-20 | `v1.0.0-arc04` | 16 discrete business modules (MOD-01 to MOD-16), pure domain models, 18 domain events, AST checks, 94 tests. |
| **[Devlog-006](devlog-006-arc05-multi-tenant-architecture.md)** | **ARC-05 Multi-Tenant Architecture & Isolation** | 2026-11-20 | `v1.0.0-arc05` | Organization primary tenancy, 8-layer defense in depth, PostgreSQL RLS, storage/cache isolation, 144 tests. |
| **[Devlog-007](devlog-007-arc06-data-architecture-and-persistence.md)** | **ARC-06 Data Architecture & Persistence Baseline** | 2026-11-20 | `v1.0.0-arc06` | Relational schema, composite FKs, 30+ SQLAlchemy models across 10 groups, immutable published snapshots, 199 tests. |
| **[Devlog-008](devlog-008-arc07-api-and-integration-architecture.md)** | **ARC-07 API & Integration Architecture** | 2026-11-21 | `v1.0.0-arc07` | REST API, 66 endpoints, OpenAPI 3.1, TypeScript SDK, server-derived tenancy, outbox webhooks, 274 tests (75 API tests). |
| **[Devlog-009](devlog-009-arc08-theme-and-customization-architecture.md)** | **ARC-08 Theme & Customization Architecture** | 2026-11-22 | `v1.0.0-arc08` | Configuration-driven, token taxonomy, 6 themes, 4 layouts, 13 components, dual-editor parity, 378 tests (104 customization tests). |
| **[Devlog-010](devlog-010-arc09-menu-rendering-architecture.md)** | **ARC-09 Menu Rendering Architecture** | 2026-11-22 | `v1.0.0-arc09` | Decoupled presentation engine, immutable published snapshots, ETag HTTP 304, Next.js dynamic routing, 92 kB JS bundle, 498 tests (120 rendering tests). |
| **[Devlog-011](devlog-011-arc10-publishing-versioning-architecture.md)** | **ARC-10 Publishing & Versioning Architecture** | 2026-11-22 | `v1.0.0-arc10` | Draft isolation, immutable snapshots, atomic activation, non-destructive rollback, transactional outbox, 92 kB JS bundle, 618 tests (120 publishing tests). |
| **[Devlog-012](devlog-012-ci-cd-quality-gates-and-jobs-remediation.md)** | **CI/CD Quality Gates & Jobs Comprehensive Remediation** | 2026-11-22 | `v1.0.0-arc10` / Patch | Ruff linting & formatting (194 files), ESLint & frozen lockfile integration, workflow dependencies, 100% green CI jobs (618/618 tests). |
| **[Devlog-013](devlog-013-arc11-infrastructure-deployment.md)** | **ARC-11 Infrastructure & Deployment Architecture** | 2026-11-23 | `v1.0.0-arc11` | Docker Compose profiles (SaaS & Appliance), non-root multi-stage builds, Nginx reverse proxy, HMAC local storage, 738 tests (120 infra tests). |
| **[Devlog-014](devlog-014-arc12-security-scalability-reliability.md)** | **ARC-12 Security, Scalability & Reliability Architecture** | 2026-11-23 | `v1.0.0-arc12` | Argon2id auth, centralized RBAC, PostgreSQL RLS defense, circuit breakers, outbox DLQ, 888 platform tests (150 security tests). |
| **[Devlog-015](devlog-015-fcd01-development-environment-foundation.md)** | **FCD-01 Development Environment & Repository Foundation** | 2026-11-23 | `v1.0.0-fcd01` | Workstation toolchain verification, monorepo standards, code quality, developer automation, and 10-document technical foundation suite. |
| **[Devlog-016](devlog-016-fcd02-application-skeleton-and-runtime-foundation.md)** | **FCD-02 Application Skeleton & Runtime Foundation** | 2026-11-23 | `v1.0.0-fcd02` | Independent FastAPI & Next.js shells (apps/web, apps/admin, apps/api), runtime lifecycles, health probes, PWA manifest, and 22-test catalogue. |
| **[Devlog-017](devlog-017-fcd03-database-foundation-and-data-access-layer.md)** | **FCD-03 Database Foundation & Data Access Layer** | 2026-11-24 | `v1.0.0-fcd03` | Persistent relational data layer, asyncpg engine, connection pooling, Alembic reversible migrations, repositories, and atomic transactions. |
| **[Devlog-018](devlog-018-fcd04-multi-tenant-core-foundation.md)** | **FCD-04 Multi-Tenant Core Foundation** | 2026-11-24 | `v1.0.0-fcd04` | Canonical organization ownership, membership models, immutable TenantContext, TenantResolver, PostgreSQL RLS, lifecycle machines, and provisioning service. |
| **[Devlog-019](devlog-019-fcd05-identity-authentication-authorization-core.md)** | **FCD-05 Identity, Authentication & Authorization Core** | 2026-11-24 | `v1.0.0-fcd05` | Decoupled identity accounts, Argon2id hashing, timing defenses, rotating refresh tokens with reuse detection, email verification, password reset, fine-grained RBAC, and platform privilege separation. |
| **[Devlog-020](devlog-020-fcd06-domain-models-shared-business-foundation.md)** | **FCD-06 Domain Models & Shared Business Foundation** | 2026-11-24 | `v1.0.0-fcd06` | Pure zero-dependency domain models, exact Decimal Money & Currency registry, operating schedules with overnight shift intervals, RestaurantProfile aggregate, synchronized TypeScript contracts, composite tenant FK & PostgreSQL RLS. |
| **[Devlog-021](devlog-021-fcd07-api-and-communication-infrastructure.md)** | **FCD-07 API & Communication Infrastructure** | 2026-11-24 | `v1.0.0-fcd07` | Modular router tree, `/api/v1` path versioning, universal response envelope, sanitized validation errors, domain error mapping, timing/security/logging middlewares, sliding window rate limiting, durable DB idempotency with RLS, frontend client & shared types, OpenAPI 3.1, 251 tests passing (100%), 90% coverage. |
| **[Devlog-022](devlog-022-fcd08-frontend-foundation-and-design-system.md)** | **FCD-08 Frontend Foundation & Design System** | 2026-11-25 | `v1.0.0-fcd08` | Monorepo design system packages (@menu-it/design-tokens, @menu-it/theme-engine, @menu-it/ui), CSS custom properties, WCAG 2.2 AA contrast calculation, ThemeProvider, compound accessible UI components, Next.js app integration, 21 technical documents, 0 type errors, 100% build & test pass. |
| **[Devlog-023](devlog-023-fcd09-core-platform-services-and-shared-utilities.md)** | **FCD-09 Core Platform Services & Shared Utilities** | 2026-11-25 | `v1.0.0-fcd09` | Centralized frozen configuration, provider-agnostic file storage (magic byte validation, non-predictable keys, RLS isolation), Jinja2 notification engine (email/in-app, autoescaping, en/hi localization), structured JSON logging with sensitive data redaction, audit event publishers, platform utilities, 26 technical documents, 296 tests passing (100%). |
| **[Devlog-024](devlog-024-fcd10-caching-background-jobs-and-event-infrastructure.md)** | **FCD-10 Caching, Background Jobs & Event Infrastructure** | 2026-11-25 | `v1.0.0-fcd10` | Redis caching abstraction, ARQ asynchronous background workers, exponential backoff with jitter retry policies, persistent DLQ with replay API, transactional event outbox, consumer inbox deduplication, persistent scheduling with IANA timezones, transaction-local PostgreSQL RLS context, 26 technical documents, 331 tests passing (100%). |

---

## 🏛️ Engineering Philosophy & Invariants

All development documented in these logs adheres strictly to the core invariants established in ARC-01 and ARC-02:
1. **Zero-Fork Customization:** Brand themes, typography, colors, and layouts are 100% data-driven; no client branches.
2. **Strict Multi-Tenant Sovereignty:** Complete cryptographic and database-level isolation between organizations.
3. **CQRS-Lite Read/Write Asymmetry:** Write paths enforce relational integrity; diner read paths serve pre-compiled immutable snapshots.
4. **Binary & Schema Parity:** Managed SaaS and Customer-Hosted Docker appliance share 100% identical domain logic and database schema.
5. **Precision & Safety:** Zero floating-point arithmetic for currency; UTC-only timestamps; explicit ORM loading.
