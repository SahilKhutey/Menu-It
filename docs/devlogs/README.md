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

---

## 🏛️ Engineering Philosophy & Invariants

All development documented in these logs adheres strictly to the core invariants established in ARC-01 and ARC-02:
1. **Zero-Fork Customization:** Brand themes, typography, colors, and layouts are 100% data-driven; no client branches.
2. **Strict Multi-Tenant Sovereignty:** Complete cryptographic and database-level isolation between organizations.
3. **CQRS-Lite Read/Write Asymmetry:** Write paths enforce relational integrity; diner read paths serve pre-compiled immutable snapshots.
4. **Binary & Schema Parity:** Managed SaaS and Customer-Hosted Docker appliance share 100% identical domain logic and database schema.
5. **Precision & Safety:** Zero floating-point arithmetic for currency; UTC-only timestamps; explicit ORM loading.
