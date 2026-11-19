# ModularMenu — Architectural Decision Register (ADR Register)

This register records all formal Architectural Decision Records (ADRs) governing the **ModularMenu** platform, in compliance with **ARC-02 Section 2 (Architectural Governance Model)**.

---

## Decision Summary Table

| ADR ID | Title | Status | Date | Primary Principles | Governing Document |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ADR-0001** | Python 3.12 & FastAPI Core Application Service | **Accepted** | 2026-11-19 | P-01, P-08, P-09 | ARC-01, ARC-02 |
| **ADR-0002** | Next.js 14 App Router (React 18 + TypeScript) Frontend | **Accepted** | 2026-11-19 | P-03, P-06, P-10 | ARC-01, ARC-02 |
| **ADR-0003** | SQLAlchemy 2.0 Async ORM with Strict Relationship Loading | **Accepted** | 2026-11-19 | P-01, P-02, P-08 | ARC-02 §4.2, §4.5 |
| **ADR-0004** | PostgreSQL 16 Relational Persistence with Row-Level Security (RLS) | **Accepted** | 2026-11-19 | P-04, P-09 | ARC-01, ARC-02 §3.4 |
| **ADR-0005** | CQRS-Lite Asymmetric Pathways with Immutable Published Snapshots | **Accepted** | 2026-11-19 | P-07, P-06 | ARC-01, ARC-02 §3.7 |
| **ADR-0006** | Configuration-Driven Presentation Engine (Zero-Fork Invariant) | **Accepted** | 2026-11-19 | P-03, P-05 | ARC-01, ARC-02 §3.3 |
| **ADR-0007** | Binary Duality: Single Container Binary for Managed SaaS & Self-Hosted | **Accepted** | 2026-11-19 | P-08, P-01 | ARC-01, ARC-02 §3.8 |
| **ADR-0008** | Fixed-Precision Numeric Representation for Monetary Values | **Accepted** | 2026-11-19 | P-09, CON-08 | ARC-02 §4.1, §4.5 |
| **ADR-0009** | RFC 7807 Problem Details for Standardized API Error Representation | **Accepted** | 2026-11-19 | P-01, P-09 | ARC-02 §4.4 |
| **ADR-0010** | CSS Custom Properties (`--theme-*`) for Dynamic Theme Rendering | **Accepted** | 2026-11-19 | P-03, P-06 | ARC-02 §4.3, §6.1 |
| **ADR-0011** | Monorepo Structure with Strict Physical Module Boundaries | **Accepted** | 2026-11-19 | P-01, P-02 | ARC-02 §10 (WP-02) |
| **ADR-0012** | Monotonically Increasing Integer Versions and SHA-256 Digesting | **Accepted** | 2026-11-19 | P-07, CON-07 | ARC-02 §3.7, §6.5 |

---

## Detailed Decision Summaries

### ADR-0001: Python 3.12 & FastAPI Core Application Service
- **Context:** ModularMenu requires high-throughput asynchronous API handling, strict data validation, automatic OpenAPI generation, and portability across both cloud-hosted multi-tenant infrastructure and resource-constrained on-premises servers.
- **Decision:** Adopt Python 3.12 with FastAPI as the backend application framework.
- **Consequences:** Native `asyncio` execution, auto-generated OpenAPI 3.1 contracts via Pydantic v2 schemas, lightweight container footprint (<150MB base).

### ADR-0002: Next.js 14 App Router (React 18 + TypeScript) Frontend
- **Context:** The frontend encompasses three distinct interface paradigms: (1) Static/SSR diner menu with sub-second mobile loading, (2) dynamic interactive 3-panel Visual Studio editor with live real-time preview, and (3) platform management portal.
- **Decision:** Standardize on Next.js 14 with TypeScript and Tailwind CSS using React App Router architecture.
- **Consequences:** Unified component ecosystem, Server Components for lightning-fast diner menu delivery, Client Components for studio editing, zero code duplication.

### ADR-0003: SQLAlchemy 2.0 Async ORM with Strict Relationship Loading
- **Context:** Async Python applications using ORMs frequently suffer from accidental blocking I/O and `MissingGreenlet` exceptions triggered by implicit lazy loading during serialization.
- **Decision:** Mandate SQLAlchemy 2.0 Async engine with explicit `lazy="raise"` on all relationship attributes. All relational joins must be explicitly declared via `selectinload` or `joinedload`.
- **Consequences:** Complete elimination of unexpected $N+1$ query cascades; deterministic database access profiles.

### ADR-0004: PostgreSQL 16 Relational Persistence with Row-Level Security (RLS)
- **Context:** Multi-tenant SaaS environments require defense-in-depth against data leakage across restaurants coexisting in a single database.
- **Decision:** Deploy PostgreSQL 16 as the primary relational persistence engine, utilizing Row-Level Security (RLS) as an immutable database-level enforcement barrier complementing application-layer filtering.
- **Consequences:** Eliminates vulnerability to accidental omissions of `WHERE restaurant_id = ...` in custom or complex queries.

### ADR-0005: CQRS-Lite Asymmetric Pathways with Immutable Published Snapshots
- **Context:** High read traffic from restaurant guests scanning QR codes at tables must not degrade database connection pools or execute relational multi-table joins on every request.
- **Decision:** Separate the administrative write path from the diner read path. Publishing compiles the active menu into a frozen, self-contained JSON snapshot stored in `menu_versions`. Diners query pre-compiled snapshots directly.
- **Consequences:** Read queries execute in <5ms; zero relational joins on diner path; instant rollback capability.

### ADR-0006: Configuration-Driven Presentation Engine (Zero-Fork Invariant)
- **Context:** Restaurants demand distinct branding (colors, typography, spacing, card styles) without the engineering overhead of managing custom CSS branches or code forks.
- **Decision:** All visual customization must be declared in validated JSON design token structures rendered at runtime by a unified layout and component engine. Custom CSS code uploads or forked repositories are strictly prohibited.
- **Consequences:** 100% platform reusability; zero maintenance overhead per onboarded restaurant; unified release cycle.

### ADR-0007: Binary Duality: Single Container Binary for Managed SaaS & Self-Hosted
- **Context:** Customers require two deployment profiles: managed SaaS and self-hosted appliance. Maintaining separate codebases or branches causes architectural divergence.
- **Decision:** The codebase compiles into a single, identical container image. Deployment profiles (SaaS vs Customer-Hosted) are activated strictly via environment configuration and pluggable adapters.
- **Consequences:** Single test pipeline; features developed once work seamlessly across both deployment targets.

### ADR-0008: Fixed-Precision Numeric Representation for Monetary Values
- **Context:** Floating-point rounding errors in pricing, taxes, discounts, or addons create financial compliance liabilities.
- **Decision:** Monetary values must be stored as `NUMERIC(12,2)` or integer minor units (paise/cents). Binary floating-point types (`float`, `double`) are banned in domain entities and schemas.
- **Consequences:** Deterministic arithmetic; financial integrity guaranteed.

### ADR-0009: RFC 7807 Problem Details for Standardized API Error Representation
- **Context:** Disparate error formats across micro-endpoints confuse clients, visual studio consumers, and monitoring agents.
- **Decision:** Standardize all API error responses on the RFC 7807 `application/problem+json` specification.
- **Consequences:** Standardized error parsing, machine-readable `type` URIs, consistent developer experience.

### ADR-0010: CSS Custom Properties (`--theme-*`) for Dynamic Theme Rendering
- **Context:** The Visual Studio requires instant preview updates as restaurant operators adjust theme tokens, without page refreshes or costly React tree re-renders.
- **Decision:** Map theme tokens directly to CSS custom properties on the root menu container.
- **Consequences:** 60fps instant visual preview updates via CSS variable mutations; zero component re-renders.

### ADR-0011: Monorepo Structure with Strict Physical Module Boundaries
- **Context:** Multi-layered applications suffer from circular imports, tight coupling, and boundary erosion if file layouts are ambiguous.
- **Decision:** Structure the repository into `backend/`, `frontend/`, `packages/`, `docs/`, and `tests/`. Enforce module boundaries via automated AST import analysis in CI.
- **Consequences:** Clear architectural separation; automated enforcement of dependency direction.

### ADR-0012: Monotonically Increasing Integer Versions and SHA-256 Digesting
- **Context:** Menu rollbacks and cache invalidation require unambiguous version lineage and tamper-proof verification.
- **Decision:** Every published snapshot receives an incrementing integer version number (`v1`, `v2`, ...) and an immutable SHA-256 payload digest.
- **Consequences:** Instant rollback via version pointer switch; cryptographic snapshot integrity verification.
