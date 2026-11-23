# ModularMenu Architecture Index

Welcome to the **ModularMenu** (Menu-It) architecture documentation index.

This platform follows a strict architectural governance hierarchy governed by formal specifications:

```
Level 1 — System Architecture
├── ARC-01: System Architecture Overview
│   └── High-level system definition, 7 external actors, system boundaries, and 10 invariants.
├── ARC-02: Architectural Principles, Standards & Constraints
│   └── 10 governing principles (P-01 to P-10), 16 constraints (CON-01 to CON-16), and 7 quality gates.
├── ARC-03: Application Architecture (Modular Monolith)
│   └── Frontend/backend separation, application/domain layers, service/repository patterns, and request lifecycles.
├── ARC-04: Modular Domain Architecture
│   └── 16 discrete business modules, bounded contexts, domain primitives, 18-event catalogue, and AST boundaries.
├── ARC-05: Multi-Tenant Architecture & Isolation Model
│   └── Organization-based tenancy, 8-layer defense in depth, PostgreSQL RLS fail-closed policies, and 50-test security suite.
├── ARC-06: Data Architecture & Persistence Baseline
│   └── Relational-first schema, composite foreign keys, PostgreSQL RLS, SQLAlchemy 2.x, immutable published snapshots, and 55-test persistence catalogue.
├── ARC-07: API & Integration Architecture
│   └── Contract-first REST API, versioned endpoints (/api/v1), OpenAPI 3.1, server-derived tenant context, TypeScript contracts, reliable outbox webhooks, and 75-test API catalogue.
├── ARC-08: Theme & Customization Architecture
│   └── Configuration-driven customization, hierarchical design tokens, 6 themes, 4 layouts, 13 components, deterministic resolver, dual-editor parity, optimistic concurrency, and 104-test customization catalogue.
├── ARC-09: Menu Rendering Architecture
│   └── Pure presentation engine, deterministic composition, 5 mandatory slots, immutable published snapshots, ETag HTTP 304, Next.js dynamic routing, 92 kB JS bundle, and 120-test rendering catalogue.
├── ARC-10: Publishing & Versioning Architecture
│   └── Draft isolation, immutable snapshots, monotonic versioning, atomic activation, non-destructive rollback, transactional outbox, and 120-test publishing catalogue.
└── ARC-11: Infrastructure & Deployment Architecture
    └── Dual deployment profiles (SaaS vs Customer-Hosted appliance), non-root container packaging, Docker Compose orchestration, Nginx reverse proxy, HMAC local storage, and 120-test infrastructure catalogue.
```

---

## 🏛️ Architecture Documentation Suite

1. **[ARC-01 — System Architecture Overview](documentation/03_System_Architecture/ARC-01_System_Architecture_Overview.md)**
   - Status: **Approved Baseline**
   - Core Model: Multi-tenant modular platform with hybrid hosting (Managed SaaS + Customer-Hosted Appliance).
   - Core Invariant: Zero code forks for brand customizations.

2. **[ARC-02 — Principles, Standards & Constraints](documentation/03_System_Architecture/ARC-02_Architectural_Principles_Standards_Constraints.md)**
   - Status: **Approved & Implemented**
   - Implementation: 32 automated test suites passing with 100% compliance.
   - Non-Negotiables: Fixed-precision decimal currency, strict `lazy="raise"` loader safety, immutable SHA-256 snapshot publishing, and RFC 7807 error envelopes.

3. **[ARC-03 — Application Architecture](documentation/03_System_Architecture/ARC-03_Application_Architecture.md)**
   - Status: **Approved & Implemented**
   - Application Model: Modular monolith with decoupled Next.js 14 frontend and FastAPI backend.
   - Structure: Layered architecture (API ➔ Application ➔ Domain ➔ Infrastructure) with dependency inversion, Repository & Unit of Work protocols, and request correlation.
   - Quality Gates: 46 automated tests passing with 100% compliance; 95.2 kB First Load JS diner bundle; 10 audit reports in `docs/reports/ARC-03/`.

4. **[ARC-04 — Modular Domain Architecture](documentation/03_System_Architecture/ARC-04_Modular_Domain_Architecture.md)**
   - Status: **Approved & Implemented**
   - Domain Model: 16 discrete business modules (MOD-01 to MOD-16) across 5 capability groups.
   - Bounded Contexts & Events: Fine-grained aggregate boundaries, pure Python domain entities, 18 domain events (EVT-001 to EVT-018), and Protocol contracts.
   - Documentation & Quality Gates: 18 architectural deliverables in `docs/architecture/ARC-04-modular-domain-architecture/`; 94 automated tests passing (including 50-test catalogue ARC04-T001 to T050); zero prohibited cross-module imports.

5. **[ARC-05 — Multi-Tenant Architecture](documentation/03_System_Architecture/ARC-05_Multi_Tenant_Architecture.md)**
   - Status: **Approved & Implemented**
   - Tenancy Model: Organization as primary tenant boundary; Restaurant as subordinate branch boundary.
   - Defense-in-Depth: 8-layer security model, server-derived immutable `TenantContext`, PostgreSQL Row-Level Security (RLS) fail-closed policies, tenant-prefixed storage keys, isolated cache namespaces, and published-only public diner resolution.
   - Documentation & Quality Gates: 24 architectural deliverables in `docs/architecture/ARC-05-multi-tenant-architecture/`; 144 automated tests passing (including 50 multi-tenant test scenarios ARC05-T001 to T050); zero cross-tenant leakage.

6. **[ARC-06 — Data Architecture](documentation/03_System_Architecture/ARC-06_Data_Architecture.md)**
   - Status: **Approved & Implemented**
   - Persistence Model: Relational-first, tenant-aware, modular persistence architecture with SQLAlchemy 2.x and Alembic.
   - Referential Integrity: Composite foreign keys `(organization_id, parent_id)` strictly rejecting cross-tenant entity linkage; transaction-local RLS policies.
   - Immutability & Financial Rigor: Immutable menu publication snapshots (`menu_versions`) with SHA-256 digests and ORM/trigger mutation guards; fixed-precision monetary minor units.
   - Documentation & Quality Gates: 27 architectural deliverables in `docs/architecture/ARC-06-data-architecture/`; 199 automated backend tests passing (including 55 data catalogue scenarios ARC06-T001 to T055); 100% schema parity across SaaS and Customer-Hosted Docker appliance.

7. **[ARC-07 — API & Integration Architecture](documentation/03_System_Architecture/ARC-07_API_Integration_Architecture.md)**
   - Status: **Approved & Implemented**
   - API Style & Routing: Contract-first REST API under `/api/v1` with 66 registered endpoints across 10 functional groups.
   - Enforceable Contracts: Generated OpenAPI 3.1 schema (`openapi.json`/`openapi.yaml`) synchronized with frontend TypeScript types (`schema.d.ts`).
   - Tenant Security: Server-derived, immutable `TenantContext` eliminating BOLA/IDOR vulnerabilities; fail-closed authorization checking against fine-grained permission catalogue.
   - Error & Resilience Standards: Standard RFC 7807/RFC 9457 Problem Details envelopes; optimistic concurrency via ETags/row_version; reliable outbox event dispatch with HMAC-SHA256 signed webhooks.
   - Documentation & Quality Gates: 27 architectural deliverables in `docs/architecture/ARC-07-api-integration-architecture/`; 274 automated backend tests passing (including 75 API catalogue scenarios ARC07-T001 to T075); 0 regressions.

8. **[ARC-08 — Theme & Customization Architecture](documentation/03_System_Architecture/ARC-08_Theme_Customization_Architecture.md)**
   - Status: **Approved & Implemented**
   - Customization Model: 100% configuration-driven, schema-validated, versioned, portable JSON customization documents with bounded limits (256 KB, 100 components, depth 10) and zero executable/script content.
   - Registries & Token Engine: 6 platform themes, 4 responsive layouts, 13 registered components; pure deterministic theme resolver ($f(\text{Theme}, \text{Overrides}) \to \text{ResolvedTokens}$) and CSS custom properties generator (`--mm-`).
   - Dual-Editor Parity & Concurrency: Settings Editor and Visual Drag-and-Drop Editor operating on the exact same JSON document; optimistic concurrency control (`If-Match` / `ETag`); immutable revision audit log and one-click restoration.
   - Documentation & Quality Gates: 28 architectural deliverables in `docs/architecture/ARC-08-theme-customization-architecture/`; 378 total automated platform tests passing (including 104 customization catalogue scenarios ARC08-T001 to T104); 100% pass rate.

9. **[ARC-09 — Menu Rendering Architecture](documentation/03_System_Architecture/ARC-09_Menu_Rendering_Architecture.md)**
   - Status: **Approved & Implemented**
   - Rendering Model: Pure decoupled presentation engine (`@modularmenu/menu-renderer`) with zero database and zero network dependencies; deterministic `RenderPlan` output.
   - Delivery Tier: Immutable published snapshots, SHA-256 ETag generation, RFC 7232 conditional GET support (HTTP 304 Not Modified), and Next.js dynamic App Router routes (`/r/[slug]/[menuSlug]`).
   - Operator Previewing: Authorized draft previews with visual watermarking (`PREVIEW MODE — Unpublished Draft`), diagnostic warnings panel, and strict `Cache-Control: private, no-store`.
   - Documentation & Quality Gates: 31 architectural deliverables in `docs/architecture/ARC-09-menu-rendering-architecture/`; 498 total automated platform tests passing (including 120 rendering catalogue scenarios ARC09-T001 to T120); 92.0 kB public First Load JS bundle; 100% pass rate.

10. **[ARC-10 — Publishing & Versioning Architecture](documentation/03_System_Architecture/ARC-10_Publishing_and_Versioning_Architecture.md)**
    - Status: **Approved & Implemented**
    - Publishing Model: Draft isolation, monotonic version numbering (`v1`, `v2`, `v3`...), immutable snapshots with canonical SHA-256 digests, and atomic transactional activation.
    - Concurrency & Rollback: Optimistic locking via `If-Match` revision checks; non-destructive rollback reactivating previous snapshots; single authoritative active publication pointer.
    - Events & Cache: Transactional Outbox pattern (`outbox_events`) for reliable lifecycle events (`MenuPublished`, `MenuRolledBack`), edge CDN cache tag invalidations, and reconciliation jobs.
    - Documentation & Quality Gates: 30 architectural deliverables in `docs/architecture/ARC-10-publishing-versioning-architecture/`; operational guides in `docs/publishing/`; 618 total automated platform tests passing (including 120 publishing catalogue scenarios ARC10-T001 to T120); 100% pass rate.

11. **[ARC-11 — Infrastructure & Deployment Architecture](documentation/03_System_Architecture/ARC-11_Infrastructure_and_Deployment_Architecture.md)**
    - Status: **Approved & Implemented**
    - Deployment Parity: Dual profile architecture (Profile C Managed SaaS multi-tenant vs Profile D Customer-Hosted appliance) sharing identical application container images and domain logic.
    - Security Hardening: Unprivileged non-root users (`UID 10001`/`1000`), read-only root filesystems, dropped capabilities (`cap_drop: [ALL]`), isolated `data-net` bridge network, Pydantic preflight configuration validation, and automated secret redaction.
    - Resilient Operations: Ephemeral non-authoritative Redis degradation, expand-and-contract zero-downtime database migrations with pre-migration backups, triple health probes (`/live`, `/ready`, `/startup`), HMAC-signed local storage URLs, and bounded worker backoff with DLQ.
    - Documentation & Quality Gates: 34 architectural specifications in `docs/architecture/ARC-11-infrastructure-deployment/`; 29 operational runbooks across `docs/deployment/`, `docs/operations/`, `docs/backup-recovery/`, and `docs/runbooks/`; 738 total automated platform tests passing (including 120 infrastructure catalogue scenarios ARC11-T001 to T120); 100% pass rate.

---

## 🛠️ Architectural Governance & Decisions

- **[ADR Register](docs/decisions/decision-register.md):** Permanent records of all major technical decisions (ADR-0001 through ADR-0221).
- **[Developer Logs (Devlogs)](docs/devlogs/README.md):** Detailed engineering chronicles for all milestones (Devlog-001 through Devlog-013).
- **[Task Execution Logs (Tasklogs)](docs/tasklogs/README.md):** Comprehensive work package execution and test verification records.
- **[Architecture Review Policy](docs/governance/architecture-review-policy.md):** Formal decision hierarchy and review authority.
- **[Compliance Checklist](docs/governance/architecture-compliance-checklist.md):** PR quality gates for principles and constraints.
- **[Domain Architecture Suite](docs/architecture/ARC-04-modular-domain-architecture/):** Detailed specifications for MOD-01 to MOD-16, workflows, and risk register.
- **[Multi-Tenant Architecture Suite](docs/architecture/ARC-05-multi-tenant-architecture/):** Complete specifications for multi-tenancy, RLS policies, threat models, and risk register.
- **[Data Architecture Suite](docs/architecture/ARC-06-data-architecture/):** Complete specifications for 30+ relational models across 10 capability groups, composite foreign keys, RLS policies, and recovery drills.
- **[API Architecture Suite](docs/architecture/ARC-07-api-integration-architecture/):** Complete specifications for 66 REST endpoints, RFC 7807 error models, OpenAPI 3.1 contracts, and outbox webhooks.
- **[Theme & Customization Architecture Suite](docs/architecture/ARC-08-theme-customization-architecture/):** Complete specifications for 6 themes, 4 layouts, 13 components, deterministic resolver, and 104-test scenario matrix.
- **[Menu Rendering Architecture Suite](docs/architecture/ARC-09-menu-rendering-architecture/):** Complete specifications for pure rendering engine, deterministic composition, 5 mandatory slots, and 120-test scenario matrix.
- **[Publishing & Versioning Architecture Suite](docs/architecture/ARC-10-publishing-versioning-architecture/):** Complete specifications for draft revisions, validation, immutable snapshots, rollback, outbox events, and 120-test scenario matrix.
- **[Infrastructure & Deployment Architecture Suite](docs/architecture/ARC-11-infrastructure-deployment/):** Complete specifications for container packaging, Compose orchestration, Nginx reverse proxy, disaster recovery, runbooks, and 120-test scenario matrix.
- **[Shared Contracts](packages/contracts/):** JSON schemas for Theme Tokens, Component Registry, Published Snapshots, and Publishing Workflows.

---

## 🚀 Execution & Verification Commands

```bash
# Run automated architecture boundary tests
make architecture-test

# Run all test suites (unit, integration, security, contract)
make test

# Run formal end-to-end product validation scenario
make validate-e2e
```
