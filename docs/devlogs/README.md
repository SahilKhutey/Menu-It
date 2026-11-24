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

---

## 🏛️ Engineering Philosophy & Invariants

All development documented in these logs adheres strictly to the core invariants established in ARC-01 and ARC-02:
1. **Zero-Fork Customization:** Brand themes, typography, colors, and layouts are 100% data-driven; no client branches.
2. **Strict Multi-Tenant Sovereignty:** Complete cryptographic and database-level isolation between organizations.
3. **CQRS-Lite Read/Write Asymmetry:** Write paths enforce relational integrity; diner read paths serve pre-compiled immutable snapshots.
4. **Binary & Schema Parity:** Managed SaaS and Customer-Hosted Docker appliance share 100% identical domain logic and database schema.
5. **Precision & Safety:** Zero floating-point arithmetic for currency; UTC-only timestamps; explicit ORM loading.
