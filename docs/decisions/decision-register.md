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
| **ADR-0013** | Modular Monolith Architecture Baseline (ARC03-D01) | **Accepted** | 2026-11-20 | P-01, P-08 | ARC-03 §2.1 |
| **ADR-0014** | Next.js 14 App Router for Frontend Applications (ARC03-D02) | **Accepted** | 2026-11-20 | P-03, P-06 | ARC-03 §3.1 |
| **ADR-0015** | FastAPI Framework for Backend Application Service (ARC03-D03) | **Accepted** | 2026-11-20 | P-01, P-09 | ARC-03 §4.1 |
| **ADR-0016** | Decoupled Frontend and Backend Processes (ARC03-D04) | **Accepted** | 2026-11-20 | P-02, P-08 | ARC-03 §2.2 |
| **ADR-0017** | Layered Backend Architecture with Inversion of Control (ARC03-D05) | **Accepted** | 2026-11-20 | P-01, P-02 | ARC-03 §4.2 |
| **ADR-0018** | Application Services Pattern for Domain Use Cases (ARC03-D06) | **Accepted** | 2026-11-20 | P-01, P-02 | ARC-03 §5.1 |
| **ADR-0019** | Abstract Repository Interfaces for Persistence (ARC03-D07) | **Accepted** | 2026-11-20 | P-02, P-08 | ARC-03 §5.2 |
| **ADR-0020** | Unit of Work Pattern for Atomic Transactions (ARC03-D08) | **Accepted** | 2026-11-20 | P-04, P-09 | ARC-03 §5.3 |
| **ADR-0021** | Strict Versioned REST APIs (`/api/v1/`) (ARC03-D09) | **Accepted** | 2026-11-20 | P-01, P-09 | ARC-03 §7.1 |
| **ADR-0022** | Generation of Frontend Contracts from OpenAPI (ARC03-D10) | **Accepted** | 2026-11-20 | P-01, P-10 | ARC-03 §7.4 |
| **ADR-0023** | Feature-Based Frontend Module Organization (ARC03-D11) | **Accepted** | 2026-11-20 | P-01, P-06 | ARC-03 §3.2 |
| **ADR-0024** | Reusable Shared Workspace Packages (ARC03-D12) | **Accepted** | 2026-11-20 | P-01, P-08 | ARC-03 §8.1 |
| **ADR-0025** | Optional Redis / Fallback In-Memory Cache (ARC03-D13) | **Accepted** | 2026-11-20 | P-08, CON-10 | ARC-03 §11.1 |
| **ADR-0026** | Centralized Configuration Validation and Lifespan Probing (ARC03-D14) | **Accepted** | 2026-11-20 | P-08, P-09 | ARC-03 §9.1 |
| **ADR-0027** | Automated AST-Based Architecture Compliance Testing (ARC03-D15) | **Accepted** | 2026-11-20 | P-01, P-02 | ARC-03 §14.4 |
| **ADR-0028** | Modular Monolith with Explicit Domain Boundaries (ARC04-D01) | **Accepted** | 2026-11-20 | P-01, P-02 | ARC-04 §1 |
| **ADR-0029** | Sixteen Logical Business Modules Decomposition (ARC04-D02) | **Accepted** | 2026-11-20 | P-01, P-02 | ARC-04 §4.1 |
| **ADR-0030** | Single Authoritative Owner Per Business Concept (ARC04-D03) | **Accepted** | 2026-11-20 | P-01, P-04 | ARC-04 §3.4 |
| **ADR-0031** | Domain Independence from Frameworks and Infrastructure (ARC04-D04) | **Accepted** | 2026-11-20 | P-02, P-08 | ARC-04 §3.3 |
| **ADR-0032** | Cross-Module Communication via Public Contracts & Protocols (ARC04-D05) | **Accepted** | 2026-11-20 | P-01, P-02 | ARC-04 §8 |
| **ADR-0033** | Prohibition of Cross-Module Direct ORM Access (ARC04-D06) | **Accepted** | 2026-11-20 | P-01, P-04 | ARC-04 §3.1, §9.3 |
| **ADR-0034** | Fine-Grained Aggregate Boundaries for Invariant Consistency (ARC04-D07) | **Accepted** | 2026-11-20 | P-01, P-05 | ARC-04 §7.3 |
| **ADR-0035** | Standardized Domain Events for Completed Business Facts (ARC04-D08) | **Accepted** | 2026-11-20 | P-01, P-09 | ARC-04 §10 |
| **ADR-0036** | In-Process Event Dispatch as Default Communication (ARC04-D09) | **Accepted** | 2026-11-20 | P-01, P-08 | ARC-04 §3.5, §10.3 |
| **ADR-0037** | Transactional Outbox for High-Reliability Operations (ARC04-D10) | **Accepted** | 2026-11-20 | P-07, P-09 | ARC-04 §11.3 |
| **ADR-0038** | Schema-Versioned Theme, Layout, and Component Configurations (ARC04-D11) | **Accepted** | 2026-11-20 | P-03, P-10 | ARC-04 §6.8, §6.10 |
| **ADR-0039** | Visual Editor Independent Draft State and Reversible Revisions (ARC04-D12) | **Accepted** | 2026-11-20 | P-06, P-07 | ARC-04 §6.12 |
| **ADR-0040** | Immutable Published Snapshots with Cryptographic SHA-256 (ARC04-D13) | **Accepted** | 2026-11-20 | P-07, CON-07 | ARC-04 §6.13 |
| **ADR-0041** | Menu Rendering Engine Complete Decoupling from Editor State (ARC04-D14) | **Accepted** | 2026-11-20 | P-06, CON-12 | ARC-04 §6.11 |
| **ADR-0042** | Graceful Degradation for Supporting and Optional Domains (ARC04-D15) | **Accepted** | 2026-11-20 | P-08, P-09 | ARC-04 §5.7 |
| **ADR-0043** | Absolute Domain Parity Across Managed SaaS and Customer-Hosted (ARC04-D16) | **Accepted** | 2026-11-20 | P-08, CON-10 | ARC-04 §2 |

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

### ADR-0013: Modular Monolith Architecture Baseline (ARC03-D01)
- **Context:** Distributed microservices introduce operational complexity, distributed transaction costs, and networking latency unsuitable for early-stage platform delivery and customer-hosted edge deployments.
- **Decision:** Build ModularMenu as a modular monolith with strictly enforced internal module boundaries and shared contracts.
- **Consequences:** Single deployable unit, straightforward local debugging, low operational overhead, seamless path to microservices later if load demands.

### ADR-0014: Next.js 14 App Router for Frontend Applications (ARC03-D02)
- **Context:** The frontend encompasses public diner rendering requiring sub-second performance and rich admin/studio editing tools.
- **Decision:** Utilize Next.js 14 App Router, standardizing server-side rendering for public diners and client components for administrative surfaces.
- **Consequences:** Excellent mobile web performance, optimized bundle sizes (<120 kB First Load JS for diner route), and unified React 18 component model.

### ADR-0015: FastAPI Framework for Backend Application Service (ARC03-D03)
- **Context:** High concurrency, asynchronous database access, and schema-driven API contracts are required for restaurant management and public menu delivery.
- **Decision:** Standardize on FastAPI with Pydantic v2 and Python 3.12.
- **Consequences:** Native asynchronous execution, automatic OpenAPI schema generation, high developer velocity, and robust type safety.

### ADR-0016: Decoupled Frontend and Backend Processes (ARC03-D04)
- **Context:** Embedding backend logic within Next.js server actions couples UI deployment with persistence logic and complicates self-hosted dual deployments.
- **Decision:** Run Next.js and FastAPI as decoupled processes communicating strictly over HTTP REST (`/api/v1/`).
- **Consequences:** Independent horizontal scaling, independent deployments, clear process isolation, and unambiguous security perimeters.

### ADR-0017: Layered Backend Architecture with Inversion of Control (ARC03-D05)
- **Context:** Direct database calls from route handlers create unmaintainable, untestable code with tight coupling to ORM implementations.
- **Decision:** Enforce four explicit layers: API ➔ Application ➔ Domain ➔ Infrastructure. Domain logic cannot import HTTP or ORM libraries; dependencies point inward.
- **Consequences:** Clean separation of concerns, high testability with in-memory test doubles, and adherence to clean architecture principles.

### ADR-0018: Application Services Pattern for Domain Use Cases (ARC03-D06)
- **Context:** Business workflows such as menu creation, publishing, and theme updates require coordinated domain operations and transaction boundaries.
- **Decision:** Encapsulate all business workflows in application use cases accepting immutable Command DTOs and returning Result DTOs.
- **Consequences:** Business use cases are fully testable without database or web server dependencies, eliminating fat controllers.

### ADR-0019: Abstract Repository Interfaces for Persistence (ARC03-D07)
- **Context:** Hardcoding SQLAlchemy session calls in domain services prevents isolated unit testing and couples business logic to database schema.
- **Decision:** Define abstract repository interfaces (Protocols) in the application layer, implemented by concrete adapters in the infrastructure layer.
- **Consequences:** In-memory repositories can be swapped in unit tests; database implementation can evolve without touching business rules.

### ADR-0020: Unit of Work Pattern for Atomic Transactions (ARC03-D08)
- **Context:** Complex operations involving multiple entities require atomic commit or rollback across repository boundaries.
- **Decision:** Implement the Unit of Work (UoW) protocol in the application layer with concrete SQLAlchemy context manager implementation.
- **Consequences:** Explicit transaction boundaries; safe rollback upon domain exceptions; no leaking of database sessions into API routes.

### ADR-0021: Strict Versioned REST APIs (`/api/v1/`) (ARC03-D09)
- **Context:** Public diners, mobile clients, and third-party integrations require backward-compatible API contracts that evolve smoothly.
- **Decision:** Mandate version prefix `/api/v1/` on all business endpoints; operational probes reside under `/health`, `/health/live`, `/health/ready`.
- **Consequences:** Predictable routing, versioning support, zero breaking changes to existing clients.

### ADR-0022: Generation of Frontend Contracts from OpenAPI (ARC03-D10)
- **Context:** Hand-crafted TypeScript types drifting from backend Pydantic models lead to runtime serialization bugs.
- **Decision:** Generate TypeScript interfaces directly from the backend OpenAPI 3.1 specification into `packages/contracts` and frontend API clients.
- **Consequences:** Single source of truth, end-to-end type safety, compile-time detection of API mismatches.

### ADR-0023: Feature-Based Frontend Module Organization (ARC03-D11)
- **Context:** Monolithic frontend component folders become unwieldy as application complexity grows.
- **Decision:** Organize frontend code into domain-specific feature folders (`src/features/menus`, `src/features/themes`, `src/features/editor`) containing local components, services, and hooks.
- **Consequences:** High cohesion, low coupling, easier code navigation, and clear feature ownership.

### ADR-0024: Reusable Shared Workspace Packages (ARC03-D12)
- **Context:** Contracts, design tokens, and theme definitions must be shared between frontend and backend without duplicating code.
- **Decision:** Maintain monorepo workspace packages (`packages/contracts`, `packages/theme-tokens`) consumed by both frontend and backend.
- **Consequences:** Zero code duplication for shared data structures, immediate feedback on schema changes.

### ADR-0025: Optional Redis / Fallback In-Memory Cache (ARC03-D13)
- **Context:** Customer-hosted environments may not provide Redis, while cloud SaaS deployments require distributed caching for scale.
- **Decision:** Make Redis optional with automatic fallback to local in-memory TTL caching when Redis is unconfigured or unavailable.
- **Consequences:** Appliance simplicity for customer-hosted installations; scalable caching for multi-tenant cloud SaaS.

### ADR-0026: Centralize Configuration Validation and Lifespan Probing (ARC03-D14)
- **Context:** Invalid or missing environment variables cause runtime failures mid-request. Operational orchestrators need granular liveness and readiness states.
- **Decision:** Validate all configuration at startup using Pydantic Settings; provide explicit `/health/live` (process alive) and `/health/ready` (database connected) probes.
- **Consequences:** Fail-fast startup on misconfiguration; accurate orchestration by Kubernetes and Docker health checks.

### ADR-0027: Automated AST-Based Architecture Compliance Testing (ARC03-D15)
- **Context:** Architectural conventions and layer boundaries degrade over time if not continuously enforced by automated tooling.
- **Decision:** Implement automated Python AST tests (`tests/architecture/`) in CI to enforce boundary rules, layer independence, and forbidden imports.
- **Consequences:** Zero architectural drift; PRs violating architectural constraints fail automatically in CI.

### ADR-0028: Modular Monolith with Explicit Domain Boundaries (ARC04-D01)
- **Context:** Premature microservices introduce network latency and distributed failure modes. A monolithic codebase without boundaries becomes an unmaintainable "big ball of mud".
- **Decision:** ModularMenu is engineered as an in-process modular monolith with strictly enforced logical boundaries.
- **Consequences:** Single deployment artifact, high developer velocity, in-memory function calls, and clear module contracts.

### ADR-0029: Sixteen Logical Business Modules Decomposition (ARC04-D02)
- **Context:** Restaurant platforms encompass authentication, restaurant operations, menu catalogs, visual customization, and publishing.
- **Decision:** Partition backend capabilities into 16 discrete modules (MOD-01 to MOD-16) across 5 capability groups.
- **Consequences:** Unambiguous code ownership, modular testability, and isolated feature evolution.

### ADR-0030: Single Authoritative Owner Per Business Concept (ARC04-D03)
- **Context:** Duplicating business authority across modules creates conflicting validation rules and data divergence.
- **Decision:** Every domain concept has exactly one authoritative owning module; other modules consume via read models or contracts.
- **Consequences:** Deterministic business invariants; single source of truth for all business operations.

### ADR-0031: Domain Independence from Frameworks and Infrastructure (ARC04-D04)
- **Context:** Embedding FastAPI, SQLAlchemy, or HTTP models into domain logic couples business rules to external dependencies.
- **Decision:** Core domain entities and value objects are pure Python dataclasses with zero external framework imports.
- **Consequences:** Sub-millisecond unit test execution, complete test independence, and clean architectural separation.

### ADR-0032: Cross-Module Communication via Public Contracts & Protocols (ARC04-D05)
- **Context:** Direct imports of peer module internal implementation classes create tight coupling.
- **Decision:** Cross-module collaboration occurs strictly via Python `typing.Protocol` interfaces and public contract schemas.
- **Consequences:** Concrete implementations can be refactored or mocked without affecting consumer modules.

### ADR-0033: Prohibition of Cross-Module Direct ORM Access (ARC04-D06)
- **Context:** Directly querying or updating another module's database tables bypasses business rules and invariants.
- **Decision:** Modules are strictly prohibited from importing peer ORM models or executing cross-module database writes.
- **Consequences:** Invariants are preserved; database table ownership is respected; enforced by CI AST checks.

### ADR-0034: Fine-Grained Aggregate Boundaries for Invariant Consistency (ARC04-D07)
- **Context:** Monolithic aggregates (e.g. Restaurant containing all menus, dishes, and media) cause locking bottlenecks.
- **Decision:** Define fine-grained aggregate roots referencing other aggregates by immutable UUID.
- **Consequences:** Minimal database lock contention; clear transaction boundaries; high concurrent throughput.

### ADR-0035: Standardized Domain Events for Completed Business Facts (ARC04-D08)
- **Context:** Side effects across modules must be traceable, auditable, and decoupled.
- **Decision:** Establish an 18-event domain catalogue (EVT-001 to EVT-018) carrying metadata, correlation IDs, and timestamps.
- **Consequences:** Comprehensive operational auditability; clean asynchronous decoupling.

### ADR-0036: In-Process Event Dispatch as Default Communication (ARC04-D09)
- **Context:** Distributed message brokers (Kafka, RabbitMQ) introduce operational burdens unsuited for single-appliance edge setups.
- **Decision:** Default to synchronous in-process event dispatching within the application memory space.
- **Consequences:** Zero external message broker dependencies; simple operations; fast execution.

### ADR-0037: Transactional Outbox for High-Reliability Operations (ARC04-D10)
- **Context:** Operations requiring dual-write consistency between database records and external message delivery.
- **Decision:** Mandate transactional outbox records only for critical events requiring guaranteed delivery.
- **Consequences:** Avoids distributed 2PC transactions while guaranteeing at-least-once delivery for critical events.

### ADR-0038: Schema-Versioned Theme, Layout, and Component Configurations (ARC04-D11)
- **Context:** Visual customizations evolve over time and must not break historical menu snapshots.
- **Decision:** All theme tokens, layout definitions, and component property schemas must be strictly versioned and validated.
- **Consequences:** Backward compatibility guaranteed; old snapshots render reliably across UI releases.

### ADR-0039: Visual Editor Independent Draft State and Reversible Revisions (ARC04-D12)
- **Context:** Operator customization experiments must not disrupt active public menus or diner experiences.
- **Decision:** The Visual Menu Editor operates on isolated drafts with reversible undo/redo revision stacks.
- **Consequences:** 100% draft isolation; active menus remain undisturbed until deliberate publication.

### ADR-0040: Immutable Published Snapshots with Cryptographic SHA-256 (ARC04-D13)
- **Context:** Menu publishing must guarantee immutability, auditability, and instant rollback capability.
- **Decision:** Publishing compiles a frozen JSON snapshot stamped with a cryptographic SHA-256 digest.
- **Consequences:** Read path requires zero relational joins; snapshots cannot be tampered with; instant rollback.

### ADR-0041: Menu Rendering Engine Complete Decoupling from Editor State (ARC04-D14)
- **Context:** Diners loading public menus must never download heavy visual editor libraries or load draft states.
- **Decision:** The Menu Rendering Engine consumes only published snapshots and styling tokens, completely isolated from editor code.
- **Consequences:** Lightweight customer mobile bundles (<120 kB JS); zero exposure of administrative tools to diners.

### ADR-0042: Graceful Degradation for Supporting and Optional Domains (ARC04-D15)
- **Context:** Network or storage failures in optional capabilities (media, analytics) must not block core menu access.
- **Decision:** Core menu management and customer rendering gracefully degrade when optional domains are unavailable.
- **Consequences:** High system resilience; menu displays text gracefully if media thumbnails fail to load.

### ADR-0043: Absolute Domain Parity Across Managed SaaS and Customer-Hosted (ARC04-D16)
- **Context:** Maintaining separate domain logic for cloud vs self-hosted customers leads to feature divergence.
- **Decision:** The domain layer is 100% identical and binary-portable across Managed SaaS and Customer-Hosted profiles.
- **Consequences:** Features built once work everywhere; single unified test suite and release cycle.


### ADR-0044: Organization is the Primary Tenant Boundary (ARC05-D01)
- **Context:** ModularMenu must support multi-branch restaurant brands, franchises, and single cafes under a coherent administrative and billing model.
- **Decision:** The `Organization` is established as the primary tenant boundary. All billing, users, permissions, custom themes, and branches belong to an organization.
- **Consequences:** Clean multi-branch hierarchy; unified tenant isolation and billing.

### ADR-0045: Restaurant is a Subordinate Resource Boundary (ARC05-D02)
- **Context:** Operators need to control branch-level menu publishing, hours, and staff permissions within an organization.
- **Decision:** The `Restaurant` is a subordinate resource boundary scoped under its parent organization.
- **Consequences:** Users can be granted organization-wide access or branch-specific permissions.

### ADR-0046: Shared Database and Shared Schema for Managed SaaS (ARC05-D03)
- **Context:** Infrastructure density and operational simplicity are essential for managed multi-tenant SaaS delivery.
- **Decision:** Managed SaaS uses a shared PostgreSQL database and shared schema, with logical partitioning via tenant columns, composite keys, and PostgreSQL RLS.
- **Consequences:** Cost-effective scalability; single migration pipeline; robust defense-in-depth isolation.

### ADR-0047: Authoritative Organization Ownership on Tenant-Owned Resources (ARC05-D04)
- **Context:** Relying solely on deep parent traversal to determine tenant ownership creates query vulnerability.
- **Decision:** Every tenant-owned database table includes an indexed `organization_id` column.
- **Consequences:** Instant O(1) tenant boundary filtering on all queries; direct RLS policy applicability.

### ADR-0048: Server-Side Membership and Role Validation (ARC05-D05)
- **Context:** Clients must never be trusted to declare their tenant ownership or assigned permissions.
- **Decision:** Membership and roles are verified authoritatively on the server from validated database records. Client-provided tenant IDs are treated strictly as selectors.
- **Consequences:** Prevents tenant ID spoofing (ARC05-TH02) and unauthorized privilege escalation.

### ADR-0049: Immutable Request-Scoped TenantContext (ARC05-D06)
- **Context:** Tenant execution context must be tamper-proof and consistent across the request execution graph.
- **Decision:** Tenant state is encapsulated in a frozen, immutable `TenantContext` dataclass constructed once per authenticated request.
- **Consequences:** Eliminates mutable state bugs; simplifies security auditing and tracing.

### ADR-0050: Explicit TenantContext Passing to Application Services (ARC05-D07)
- **Context:** Hidden thread-local state can introduce subtle context leakage in asynchronous Python runtimes.
- **Decision:** `TenantContext` is explicitly passed as a parameter to application use cases, command handlers, and queries.
- **Consequences:** Clear architectural contracts; high unit-testability; explicit authorization requirements.

### ADR-0051: Repository Queries Enforce Tenant Scope (ARC05-D08)
- **Context:** Accidental unscoped database queries risk exposing data across tenants.
- **Decision:** Repositories require `TenantContext` and mandate `organization_id` scoping on all reads, mutations, and deletions.
- **Consequences:** Unscoped SQL queries are structurally eliminated at the application repository layer.

### ADR-0052: PostgreSQL Row-Level Security for Defense-in-Depth (ARC05-D09)
- **Context:** Application bugs or manual SQL scripts must not compromise multi-tenant isolation.
- **Decision:** PostgreSQL RLS is enabled and forced (`FORCE ROW LEVEL SECURITY`) across all tenant-owned tables.
- **Consequences:** Database hardware-level safety net; queries without tenant context fail closed.

### ADR-0053: Restricted Runtime Database Role Cannot Bypass RLS (ARC05-D10)
- **Context:** If the runtime database user possesses superuser or bypassrls privileges, RLS policies are rendered ineffective.
- **Decision:** The runtime application database role (`modularmenu_app`) is created with `NOSUPERUSER` and `NOBYPASSRLS`.
- **Consequences:** Guarantees that RLS policies are strictly enforced on all application database connections.

### ADR-0054: Transaction-Local PostgreSQL Setting for Tenant Context (ARC05-D11)
- **Context:** Connection pooling (e.g. PgBouncer / SQLAlchemy pool) can leak session state across requests if not cleaned up.
- **Decision:** Tenant identity is bound using transaction-scoped setting `SELECT set_config('app.current_organization_id', :org_id, true)`.
- **Consequences:** Context automatically disappears on transaction completion (COMMIT or ROLLBACK); zero connection pool cross-talk.

### ADR-0055: Composite Relational Foreign Keys Enforce Matching Ownership (ARC05-D12)
- **Context:** Attaching child records (categories, items) to foreign parent records across tenants must be prevented.
- **Decision:** Database schemas enforce composite foreign keys `(organization_id, parent_id)`.
- **Consequences:** Cross-tenant entity attachment is rejected by database relational integrity rules.

### ADR-0056: Storage Object Keys Enforce Tenant Scope (ARC05-D13)
- **Context:** Object storage endpoints can become cross-tenant leakage vectors if keys are guessable or client-defined.
- **Decision:** Storage keys are server-generated using canonical prefix `media/organizations/{org_id}/...`, and private downloads require HMAC-signed URLs.
- **Consequences:** Complete media isolation; prevention of arbitrary bucket traversal and enumeration.

### ADR-0057: Tenant-Specific Cache Keys and Isolated Namespaces (ARC05-D14)
- **Context:** Shared caching layers (Redis/memory) must never return cached data from one tenant to another.
- **Decision:** All tenant-specific cache keys enforce prefix `tenant:{organization_id}:...`, and tenant switching triggers immediate cache eviction.
- **Consequences:** Zero cache collisions; instant invalidation upon tenant role or membership changes.

### ADR-0058: Public Menu Delivery Restricted to Published Snapshots (ARC05-D15)
- **Context:** Public diners must browse active menus without creating accounts, but must never access internal tenant data or drafts.
- **Decision:** Public menu endpoints only resolve active, immutable published snapshots (`MOD-13`), never draft tables (`MOD-12`).
- **Consequences:** Public access is decoupled from tenant authentication; complete draft privacy.

### ADR-0059: Background Jobs Carry Explicit TenantJobContext (ARC05-D16)
- **Context:** Asynchronous workers executing queued tasks must preserve the same tenant boundaries as HTTP requests.
- **Decision:** Background job envelopes carry an immutable `TenantJobContext`, validate target resource ownership, and clean up context in worker processes.
- **Consequences:** Background worker isolation verified; prevention of pooled worker context leakage.

### ADR-0060: Platform Administration Strictly Separated from Tenant Roles (ARC05-D17)
- **Context:** Platform staff privileges must not grant unrestricted access to customer menus or settings.
- **Decision:** Platform operator roles and tenant roles are completely separate security domains.
- **Consequences:** Platform administration cannot silently bypass business authorization or tenant policies.

### ADR-0061: Formal Tenant Lifecycle with Suspension Grace Policies (ARC05-D18)
- **Context:** Non-payment or account suspension must halt administrative modifications without immediately breaking public diner menus.
- **Decision:** Tenant state machine includes active, suspended, and offboarded states. Public menus observe a documented grace policy during suspension.
- **Consequences:** Smooth operational handling; protects diners while enforcing subscription boundaries.

### ADR-0062: Time-Bounded, Audited Support Operator Access (ARC05-D19)
- **Context:** Customer support troubleshooting requires controlled inspection of customer data without permanent superuser access.
- **Decision:** Support access requires explicit customer authorization, short-lived session grants, and exhaustive audit logging.
- **Consequences:** Transparent, secure customer support without backdoors or unmonitored access.

### ADR-0063: SaaS and Self-Hosted Share Identical Domain Authorization Rules (ARC05-D20)
- **Context:** Architectural drift between cloud SaaS and customer-hosted appliance deployments increases maintenance burden.
- **Decision:** The core domain entities, authorization policies, and TenantContext interfaces are 100% identical across SaaS and Customer-Hosted editions.
- **Consequences:** Features and security policies developed once operate identically in all deployment profiles.
