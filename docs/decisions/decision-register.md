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

| **ADR-0192** | Docker Compose v2 as Primary Orchestration Engine (ARC11-D01) | **Accepted** | 2026-11-23 | P-08, P-01 | ARC-11 §5.1 |
| **ADR-0193** | Unified Multi-Stage Container Images for SaaS & Customer-Hosted (ARC11-D02) | **Accepted** | 2026-11-23 | P-08, CON-10 | ARC-11 §4.1 |
| **ADR-0194** | Unprivileged Non-Root Execution across All Containers (ARC11-D03) | **Accepted** | 2026-11-23 | P-09, CON-09 | ARC-11 §4.2 |
| **ADR-0195** | Read-Only Root Filesystem with Ephemeral tmpfs Mounts (ARC11-D04) | **Accepted** | 2026-11-23 | P-09, P-08 | ARC-11 §5.3 |
| **ADR-0196** | Strictly Ephemeral Redis with Graceful In-Memory Degradation (ARC11-D05) | **Accepted** | 2026-11-23 | P-08, CON-10 | ARC-11 §5.4 |
| **ADR-0197** | Expand-and-Contract Zero-Downtime Database Migration Protocol (ARC11-D06) | **Accepted** | 2026-11-23 | P-07, P-09 | ARC-11 §8.2 |
| **ADR-0198** | HMAC SHA-256 Signed URLs for Local Filesystem Object Storage (ARC11-D07) | **Accepted** | 2026-11-23 | P-04, P-09 | ARC-11 §10.2 |
| **ADR-0199** | Explicit TenantJobContext Envelope Required for Worker Jobs (ARC11-D08) | **Accepted** | 2026-11-23 | P-04, P-07 | ARC-11 §9.2 |
| **ADR-0200** | Mandatory Pre-Migration Database Snapshot and Verification (ARC11-D09) | **Accepted** | 2026-11-23 | P-07, P-09 | ARC-11 §8.3 |
| **ADR-0201** | Triple Health Probe Model (/live, /ready, /startup) (ARC11-D10) | **Accepted** | 2026-11-23 | P-01, P-08 | ARC-11 §11.1 |
| **ADR-0202** | Strict Environment Preflight Validation via Pydantic Settings (ARC11-D11) | **Accepted** | 2026-11-23 | P-08, P-09 | ARC-11 §7.1 |
| **ADR-0203** | Automated Secret Redaction in Logs, Exceptions, and Dumps (ARC11-D12) | **Accepted** | 2026-11-23 | P-09, CON-09 | ARC-11 §7.2 |
| **ADR-0204** | Next.js 14 Standalone Mode with < 120 kB First Load JS Budget (ARC11-D13) | **Accepted** | 2026-11-23 | P-03, P-06 | ARC-11 §4.3 |
| **ADR-0205** | Python 3.12 Slim Debian Bookworm Standardized Base Image (ARC11-D14) | **Accepted** | 2026-11-23 | P-01, P-08 | ARC-11 §4.4 |
| **ADR-0206** | Nginx Reverse Proxy for TLS 1.3 Termination and Rate Limiting (ARC11-D15) | **Accepted** | 2026-11-23 | P-08, P-09 | ARC-11 §6.1 |
| **ADR-0207** | Dropping All Linux Capabilities (`cap_drop: [ALL]`) in Production (ARC11-D16) | **Accepted** | 2026-11-23 | P-09, CON-09 | ARC-11 §5.5 |
| **ADR-0208** | Isolated Internal Bridge Networks for Data Persistence Layer (ARC11-D17) | **Accepted** | 2026-11-23 | P-04, P-09 | ARC-11 §16.1 |
| **ADR-0209** | Bounded Exponential Backoff and Dead-Letter Queue in Worker (ARC11-D18) | **Accepted** | 2026-11-23 | P-07, P-08 | ARC-11 §9.3 |
| **ADR-0210** | Path Traversal Normalization Guard in Local Storage Adapter (ARC11-D19) | **Accepted** | 2026-11-23 | P-04, P-09 | ARC-11 §10.3 |
| **ADR-0211** | Encrypted Off-Host Backup Storage with 1h RPO and 4h RTO (ARC11-D20) | **Accepted** | 2026-11-23 | P-07, P-09 | ARC-11 §12.1 |
| **ADR-0212** | GitHub Actions Automated Quality Gates with 100% Test Pass Gate (ARC11-D21) | **Accepted** | 2026-11-23 | P-01, P-02 | ARC-11 §13.1 |
| **ADR-0213** | Explicit Manual Approval Gate for Production SaaS Deployments (ARC11-D22) | **Accepted** | 2026-11-23 | P-08, P-09 | ARC-11 §13.2 |
| **ADR-0214** | Turnkey Single-Command Customer Appliance Offline Installation (ARC11-D23) | **Accepted** | 2026-11-23 | P-08, CON-10 | ARC-11 §14.1 |
| **ADR-0215** | Bounded 10 MB Maximum File Size for Media Ingestion (ARC11-D24) | **Accepted** | 2026-11-23 | P-08, P-09 | ARC-11 §10.4 |
| **ADR-0216** | Sanitized Database Error Responses on Probe Failures (ARC11-D25) | **Accepted** | 2026-11-23 | P-09, CON-09 | ARC-11 §11.2 |
| **ADR-0217** | Transactional Outbox Queue Lag Growth Telemetry (ARC11-D26) | **Accepted** | 2026-11-23 | P-07, P-08 | ARC-11 §9.4 |
| **ADR-0218** | Minimum 20 GB Disk Space Preflight Enforcement (ARC11-D27) | **Accepted** | 2026-11-23 | P-08, P-09 | ARC-11 §18.2 |
| **ADR-0219** | Automated 30-Day TLS Certificate Expiry Alerting (ARC11-D28) | **Accepted** | 2026-11-23 | P-08, P-09 | ARC-11 §6.3 |
| **ADR-0220** | Semi-Annual Simulated Disaster Recovery Restore Drills (ARC11-D29) | **Accepted** | 2026-11-23 | P-07, P-09 | ARC-11 §12.3 |
| **ADR-0221** | Automated Release Verification Smoke Suite Post-Deployment (ARC11-D30) | **Accepted** | 2026-11-23 | P-01, P-08 | ARC-11 §13.3 |
| **ADR-0222** | Argon2id for Password Storage Hashing (ARC12-D01) | **Accepted** | 2026-11-23 | P-09, SEC-01 | ARC-12 §5.1 |
| **ADR-0223** | Cryptographic 256-bit CSPRNG Session Identifiers (ARC12-D02) | **Accepted** | 2026-11-23 | P-09, SEC-01 | ARC-12 §5.1 |
| **ADR-0224** | Immediate Session Rotation on Privilege Elevation (ARC12-D03) | **Accepted** | 2026-11-23 | P-09, SEC-01 | ARC-12 §5.1 |
| **ADR-0225** | __Host- Cookie Prefixes in Production Environments (ARC12-D04) | **Accepted** | 2026-11-23 | P-09, SEC-01 | ARC-12 §5.1 |
| **ADR-0226** | Centralized RBAC Permission Table Mapping (ARC12-D05) | **Accepted** | 2026-11-23 | P-04, P-09 | ARC-12 §5.2 |
| **ADR-0227** | Organization-Scoped Tenant Context Resolution (ARC12-D06) | **Accepted** | 2026-11-23 | P-04, P-09 | ARC-12 §5.3 |
| **ADR-0228** | Force Row Level Security on Tenant Database Tables (ARC12-D07) | **Accepted** | 2026-11-23 | P-04, P-09 | ARC-12 §5.3 |
| **ADR-0229** | Non-Bypass Application Database Runtime Role (ARC12-D08) | **Accepted** | 2026-11-23 | P-04, P-09 | ARC-12 §5.3 |
| **ADR-0230** | Dual-Layer Tenant Isolation Guardrails (App + DB) (ARC12-D09) | **Accepted** | 2026-11-23 | P-04, P-09 | ARC-12 §5.3 |
| **ADR-0231** | Anti-CSRF Token Validation with Bearer Exemption (ARC12-D10) | **Accepted** | 2026-11-23 | P-09, SEC-02 | ARC-12 §5.4 |
| **ADR-0232** | Strict Content Security Policy (CSP) Rules (ARC12-D11) | **Accepted** | 2026-11-23 | P-09, SEC-02 | ARC-12 §5.4 |
| **ADR-0233** | Automated Security Response Headers Standard (ARC12-D12) | **Accepted** | 2026-11-23 | P-09, SEC-02 | ARC-12 §5.4 |
| **ADR-0234** | SSRF Outbound Network Request Guard (ARC12-D13) | **Accepted** | 2026-11-23 | P-09, SEC-02 | ARC-12 §5.4 |
| **ADR-0235** | Strict Media Magic Byte File Signature Verification (ARC12-D14) | **Accepted** | 2026-11-23 | P-09, SEC-03 | ARC-12 §5.5 |
| **ADR-0236** | 25 Megapixel Limit for Decompression Bomb Defense (ARC12-D15) | **Accepted** | 2026-11-23 | P-08, P-09 | ARC-12 §5.5 |
| **ADR-0237** | Canonical Object Key Isolation for Tenant Media (ARC12-D16) | **Accepted** | 2026-11-23 | P-04, P-09 | ARC-12 §5.5 |
| **ADR-0238** | Webhook HMAC SHA-256 Cryptographic Verification (ARC12-D17) | **Accepted** | 2026-11-23 | P-09, SEC-04 | ARC-12 §5.6 |
| **ADR-0239** | Webhook Timestamp Drift Tolerance Limit (300s) (ARC12-D18) | **Accepted** | 2026-11-23 | P-09, SEC-04 | ARC-12 §5.6 |
| **ADR-0240** | Webhook Idempotency & Replay Attack Defense (ARC12-D19) | **Accepted** | 2026-11-23 | P-07, P-09 | ARC-12 §5.6 |
| **ADR-0241** | Immutable Append-Only Audit Logging Ledger (ARC12-D20) | **Accepted** | 2026-11-23 | P-09, SEC-05 | ARC-12 §5.7 |
| **ADR-0242** | Automated Regex Credential Masking in Logs and Traces (ARC12-D21) | **Accepted** | 2026-11-23 | P-09, SEC-05 | ARC-12 §5.7 |
| **ADR-0243** | Non-Root Application Container Execution (UID 1001) (ARC12-D22) | **Accepted** | 2026-11-23 | P-08, P-09 | ARC-12 §5.8 |
| **ADR-0244** | Dropped Linux Capabilities in Production Containers (ARC12-D23) | **Accepted** | 2026-11-23 | P-08, P-09 | ARC-12 §5.8 |
| **ADR-0245** | Isolated Internal Bridge Networks for Data Stores (ARC12-D24) | **Accepted** | 2026-11-23 | P-08, P-09 | ARC-12 §5.8 |
| **ADR-0246** | Multi-Tier Token Bucket Rate Limiting (ARC12-D25) | **Accepted** | 2026-11-23 | P-07, P-09 | ARC-12 §6.1 |
| **ADR-0247** | Public Menu Immutable Pre-Rendered CDN Snapshot Caching (ARC12-D26) | **Accepted** | 2026-11-23 | P-06, P-07 | ARC-12 §6.1 |
| **ADR-0248** | Frontend 120 kB Gzip Initial JavaScript Budget (ARC12-D27) | **Accepted** | 2026-11-23 | P-02, P-07 | ARC-12 §6.4 |
| **ADR-0249** | Database Connection Pool Boundaries (20 Pool, 10 Overflow) (ARC12-D28) | **Accepted** | 2026-11-23 | P-07, P-08 | ARC-12 §6.2 |
| **ADR-0250** | Composite Indexing on Multi-Tenant Database Columns (ARC12-D29) | **Accepted** | 2026-11-23 | P-04, P-07 | ARC-12 §6.2 |
| **ADR-0251** | Transactional Outbox Pattern for Durable Asynchronous Events (ARC12-D30) | **Accepted** | 2026-11-23 | P-07, P-08 | ARC-12 §6.3 |
| **ADR-0252** | Bounded Exponential Backoff with Full Uniform Jitter (ARC12-D31) | **Accepted** | 2026-11-23 | P-07, P-08 | ARC-12 §6.3 |
| **ADR-0253** | Poison Pill Dead-Letter Queue Quarantine after 8 Attempts (ARC12-D32) | **Accepted** | 2026-11-23 | P-07, P-08 | ARC-12 §6.3 |
| **ADR-0254** | Three-State Circuit Breakers for External Integrations (ARC12-D33) | **Accepted** | 2026-11-23 | P-07, P-08 | ARC-12 §7.1 |
| **ADR-0255** | Ephemeral Redis Resilient Graceful Degradation (ARC12-D34) | **Accepted** | 2026-11-23 | P-07, P-08 | ARC-12 §7.2 |
| **ADR-0256** | Disaster Recovery RPO <= 1h and RTO <= 4h Standards (ARC12-D35) | **Accepted** | 2026-11-23 | P-07, P-09 | ARC-12 §7.4 |

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

### ADR-0064: PostgreSQL Primary Relational Persistence (ARC06-D01)
- **Context:** ModularMenu requires robust relational integrity, composite foreign key enforcement, row-level security, transactional guarantees, and JSONB validation.
- **Decision:** PostgreSQL (>=15) is selected as the primary relational database across both SaaS and customer-hosted deployments.
- **Consequences:** Consistent, standards-compliant relational semantics; support for native UUIDs, TIMESTAMPTZ, and RLS.

### ADR-0065: Shared Logical Database Schema for Managed SaaS (ARC06-D02)
- **Context:** SaaS operations require high multi-tenant operational density, unified schema migrations, and simplified connection pooling.
- **Decision:** Multi-tenant SaaS operates on a single PostgreSQL database with a shared logical schema, partitioned logically by explicit tenant keys.
- **Consequences:** Operational simplicity during schema migrations; mandates strict tenant filtering at query and RLS levels.

### ADR-0066: UUIDv4 Primary Identifiers (ARC06-D03)
- **Context:** Sequential integer IDs expose enumeration attack vectors and complicate distributed generation and data migration.
- **Decision:** All database entities use random UUIDv4 identifiers as surrogate primary keys.
- **Consequences:** Unpredictable resource identifiers; client/service generation without database round-trips.

### ADR-0067: Organization-Level Tenant Ownership Boundary (ARC06-D04)
- **Context:** Multi-branch operations require a top-level commercial and legal tenant boundary that owns all restaurants and user memberships.
- **Decision:** Organization (organizations) is the primary tenant boundary (organization_id).
- **Consequences:** All tenant isolation policies, billing, and organizational memberships anchor to organization_id.

### ADR-0068: Restaurant as Subordinate Resource to Organization (ARC06-D05)
- **Context:** A brand or hospitality group owns multiple restaurant locations or branches.
- **Decision:** Restaurant (
estaurants) is strictly subordinate to an organization, carrying both organization_id and id.
- **Consequences:** Restaurants cannot exist outside an organization; multi-branch operations share billing and asset ownership.

### ADR-0069: Explicit organization_id on All Tenant-Owned Records (ARC06-D06)
- **Context:** Joining up the relational graph to determine tenant ownership causes security vulnerabilities and query latency.
- **Decision:** Every tenant-owned table must include an explicit, non-nullable organization_id column.
- **Consequences:** Enables single-column tenant indexing, row-level security policies, and direct cross-tenant isolation enforcement.

### ADR-0070: Explicit restaurant_id on Restaurant-Scoped Records (ARC06-D07)
- **Context:** Menus, categories, items, and design configurations belong to a specific restaurant branch.
- **Decision:** Restaurant-scoped records include an explicit 
estaurant_id column alongside organization_id.
- **Consequences:** Direct branch querying and dual-scope authorization without traversal joins.

### ADR-0071: Composite Relational Foreign Keys Enforce Matching Ownership (ARC06-D08)
- **Context:** An entity in organization A must never be attached to a parent or menu in organization B.
- **Decision:** Foreign key relationships enforce composite constraints (organization_id, parent_id).
- **Consequences:** Cross-tenant entity attachment is rejected directly at the database engine level.

### ADR-0072: SQLAlchemy 2.x Declarative ORM Baseline (ARC06-D09)
- **Context:** Modular monolith backend requires type-safe query formulation, async I/O, declarative mappings, and lifecycle events.
- **Decision:** Adopt SQLAlchemy 2.x with AsyncAttrs, Mapped, and mapped_column type annotations.
- **Consequences:** Compile-time type verification, async connection pooling, and standardized lifecycle event listeners.

### ADR-0073: Alembic for Database Migrations (ARC06-D10)
- **Context:** Database schema evolution across SaaS and Customer-Hosted deployments must be deterministic, versioned, and reversible.
- **Decision:** Use Alembic with reversible upgrade() and downgrade() steps, discovering all modular models via unified metadata.
- **Consequences:** Deterministic schema rollouts and zero drift between cloud and on-premise deployments.

### ADR-0074: Validated, Versioned JSONB for Visual Presentation Configuration (ARC06-D11)
- **Context:** Theme tokens, layout options, and component visibility require schema flexibility without altering relational tables.
- **Decision:** Use PostgreSQL JSONB exclusively for validated, versioned presentation configs; strictly prohibited for core business relationships.
- **Consequences:** Schema flexibility for UI customization while preserving relational rigor for core domain entities.

### ADR-0075: Fixed-Precision Monetary Representation (ARC06-D12)
- **Context:** IEEE 754 floating-point types cause rounding discrepancies and financial errors in menu pricing.
- **Decision:** Prices are represented as integer minor units (paise/cents) or explicit NUMERIC(12,2); floats are strictly forbidden.
- **Consequences:** Exact financial calculations across all currency operations and published snapshots.

### ADR-0076: UTC Timestamps for All Temporal Data (ARC06-D13)
- **Context:** Restaurants operate across diverse time zones; inconsistent offsets cause scheduling and auditing defects.
- **Decision:** All timestamps use PostgreSQL TIMESTAMPTZ and are generated, stored, and exchanged exclusively in UTC.
- **Consequences:** Ambiguity-free temporal sequencing, audit logging, and publication scheduling.

### ADR-0077: Defense-in-Depth Tenant Isolation with PostgreSQL RLS (ARC06-D14)
- **Context:** Relying solely on application-level WHERE organization_id = ... risks data leakage from query bugs or raw SQL execution.
- **Decision:** Combine application-level tenant filtering with PostgreSQL Row-Level Security policies on all tenant tables.
- **Consequences:** Multi-layered security; even unintended application queries cannot read or write foreign tenant data.

### ADR-0078: Transaction-Local PostgreSQL Tenant Session Context (ARC06-D15)
- **Context:** PostgreSQL RLS requires a trusted session variable indicating the authenticated tenant on shared connection pools.
- **Decision:** Unit of Work sets transaction-local pp.current_organization_id using is_local=true via set_config().
- **Consequences:** Zero connection pool leakage across pooled connections; context automatically clears on transaction commit or rollback.

### ADR-0079: Immutable Menu Publication Snapshots (ARC06-D16)
- **Context:** Subsequent draft menu edits or pricing updates must never mutate or destabilize live or historic customer menus.
- **Decision:** Menu publications create immutable, versioned snapshots (menu_versions) with canonical SHA-256 digests and mutation guards.
- **Consequences:** Historical auditability, instant rollback capabilities, and tamper-proof public rendering.

### ADR-0080: Explicit Tenant Scoping in Repositories (ARC06-D17)
- **Context:** Generic ORM query methods (session.get(Model, id)) omit tenant filters, risking cross-tenant object access.
- **Decision:** Repository interfaces require explicit organization_id parameters and enforce tenant scoping in all queries.
- **Consequences:** Impossible for application developers to perform unscoped lookups on tenant-owned entities.

### ADR-0081: Use-Case-Scoped Transaction Boundaries (ARC06-D18)
- **Context:** Long-lived transactions or multi-transaction use cases cause connection exhaustion, deadlocks, and inconsistent state.
- **Decision:** Transactions are managed via Unit of Work, exactly matching the lifecycle of a single application use case.
- **Consequences:** Atomic, consistent operations with bounded transaction lifecycles and automatic rollback on failure.

### ADR-0082: Optimistic Concurrency Control via row_version (ARC06-D19)
- **Context:** Concurrent updates from multiple restaurant managers can cause lost updates without locking entire tables.
- **Decision:** Editable draft entities include a integer 
ow_version column incremented on every update and checked on save.
- **Consequences:** Prevents lost updates with high concurrency and zero pessimistic row locking overhead.

### ADR-0083: Transactional Outbox for Reliable Event Dispatch (ARC06-D20)
- **Context:** Dual writes to the database and external message brokers cause silent event loss on application crashes.
- **Decision:** Domain events are committed atomically to an outbox_events table within the business transaction.
- **Consequences:** Guaranteed at-least-once message delivery and decoupling of domain transactions from external message queues.

### ADR-0084: Controlled Data Deletion and Retention Lifecycle (ARC06-D21)
- **Context:** Immediate cascading deletes of tenant data risk accidental data loss and compliance violations.
- **Decision:** Enforce structured lifecycle states (ctive, suspended, offboarded), grace periods, and soft-delete before purge.
- **Consequences:** Reversible operations during disputes, customer recovery grace periods, and GDPR/compliance auditability.

### ADR-0085: Decoupled Public Menu Read Model (ARC06-D22)
- **Context:** Public diners browsing menus generate read traffic that should not query normalized draft tables or require tenant auth.
- **Decision:** Public menu endpoints resolve active publication snapshots directly without tenant auth or relational draft joins.
- **Consequences:** High-performance caching, negligible database load, and zero exposure of draft or unpublished changes.

### ADR-0086: Object Storage for Media Bytes and PostgreSQL for Metadata (ARC06-D23)
- **Context:** Storing large image/media binaries in PostgreSQL Blobs causes database bloat and performance degradation.
- **Decision:** Media binaries reside in S3-compatible object storage; PostgreSQL stores strictly typed metadata and tenant paths.
- **Consequences:** Optimized relational storage, high-throughput media serving via CDN, and tenant-scoped media quotas.

### ADR-0087: Repeatable, Tested Backup and Restore Procedures (ARC06-D24)
- **Context:** Backups that are never tested fail unexpectedly during disaster recovery incidents.
- **Decision:** Automated daily logical and continuous physical backups with periodic, automated restore verification drills.
- **Consequences:** Documented, proven Recovery Time Objectives (RTO < 4h) and Recovery Point Objectives (RPO < 1h).

### ADR-0088: 100% Schema and Binary Parity Across SaaS and Customer-Hosted Editions (ARC06-D25)
- **Context:** Maintaining separate database architectures for cloud and self-hosted environments doubles testing and maintenance costs.
- **Decision:** Both editions run identical SQLAlchemy models, Alembic migrations, constraints, and seed routines.
- **Consequences:** Zero architectural bifurcation; self-hosted customers receive enterprise-grade security and data rigor out of the box.

### ADR-0089: RESTful API Architectural Style (ARC07-D01)
- **Context:** ModularMenu requires a proven, universally supported communication standard across web, mobile, and third-party consumers.
- **Decision:** ModularMenu adopts standard RESTful HTTP APIs with resource-oriented URIs, standard HTTP verbs, and JSON payloads.
- **Consequences:** Maximized developer familiarity, universal HTTP client support, predictable caching semantics, and decoupled client-server lifecycles.

### ADR-0090: Mandatory HTTPS Transport Security (ARC07-D02)
- **Context:** Unencrypted network traffic exposes authentication credentials, tenant IDs, and business data to eavesdropping and tampering.
- **Decision:** All API communication is strictly encrypted via TLS 1.3 in production with HSTS enforcement.
- **Consequences:** Complete confidentiality and integrity of all in-transit requests and responses.

### ADR-0091: JSON Payload Encoding (ARC07-D03)
- **Context:** A standardized data interchange format is required across all API endpoints.
- **Decision:** UTF-8 JSON is the exclusive data interchange format for all structured request and response bodies.
- **Consequences:** Consistent serialization, broad language interoperability, and human-readable debugging.

### ADR-0092: URI Path Versioning (/api/v1) (ARC07-D04)
- **Context:** API evolution requires deterministic version routing without silent breaking changes.
- **Decision:** API versions are explicitly prefixed in the URI path (/api/v1/). Breaking changes require a major version increment.
- **Consequences:** Transparent endpoint routing, zero header ambiguity, and smooth consumer migration pathways.

### ADR-0093: OpenAPI 3.1 Contract-First Generation (ARC07-D05)
- **Context:** Maintaining manual API documentation leads to inevitable drift between implementation and docs.
- **Decision:** OpenAPI 3.1 schemas are derived directly from FastAPI endpoint definitions and Pydantic schemas.
- **Consequences:** Guaranteed synchronization between runtime code, documentation, and client SDK contracts.

### ADR-0094: FastAPI as Canonical Backend Framework (ARC07-D06)
- **Context:** High-performance asynchronous API execution with automated schema validation is required.
- **Decision:** FastAPI is the canonical Python backend framework across both SaaS and customer-hosted editions.
- **Consequences:** Native async/await concurrency, automatic OpenAPI documentation, and dependency injection architecture.

### ADR-0095: Pydantic v2 Request Validation (ARC07-D07)
- **Context:** Invalid or malicious request payloads must be rejected before reaching service logic.
- **Decision:** All incoming request bodies, query parameters, and path variables are validated via strict Pydantic v2 schemas.
- **Consequences:** Fail-fast validation with detailed field-level error messages and zero malformed entity propagation.

### ADR-0096: Generated TypeScript Client Contracts (ARC07-D08)
- **Context:** Manual TypeScript interface authoring in frontend applications causes contract drift and runtime errors.
- **Decision:** Frontend TypeScript types are generated automatically from the backend OpenAPI schema.
- **Consequences:** Compile-time type safety across frontend network boundaries and immediate notification of backend contract changes.

### ADR-0097: Server-Managed Cookie Sessions for First-Party Web (ARC07-D09)
- **Context:** Storing JWTs in browser localStorage makes web applications vulnerable to XSS token exfiltration.
- **Decision:** First-party Next.js web applications use HttpOnly, SameSite=Lax, Secure session cookies.
- **Consequences:** Complete immunity to JavaScript token theft and transparent browser session management.

### ADR-0098: Scoped Credentials for External API Consumers (ARC07-D10)
- **Context:** Third-party integrations require programmatic access without interactive session cookies.
- **Decision:** External consumers authenticate using cryptographically signed, scoped tokens with explicit revocation and expiry.
- **Consequences:** Fine-grained API delegation, secure machine-to-machine communication, and immediate revocation capability.

### ADR-0099: Centralized Application-Level Authorization (ARC07-D11)
- **Context:** Decentralized permission checks across route handlers lead to authorization bypass vulnerabilities.
- **Decision:** Authorization policies are centrally evaluated via FastAPI dependencies using the fine-grained permission catalogue.
- **Consequences:** Enforceable, auditable security boundaries with fail-closed default behavior.

### ADR-0100: Server-Derived Immutable Tenant Context (ARC07-D12)
- **Context:** Relying on client-supplied tenant identifiers enables Broken Object Level Authorization (BOLA/IDOR) exploits.
- **Decision:** TenantContext is derived strictly on the server from authenticated sessions and active database memberships.
- **Consequences:** Complete prevention of tenant spoofing; client-supplied organization IDs act strictly as selectors.

### ADR-0101: RFC 7807 / RFC 9457 Problem Details Error Standard (ARC07-D13)
- **Context:** Inconsistent error formats create fragile frontend error handling and poor developer experience.
- **Decision:** All 4xx and 5xx API responses strictly adhere to the RFC 7807 / RFC 9457 Problem Details specification.
- **Consequences:** Standardized machine-parseable error codes, request correlation IDs, and structured field-level invalid parameters.

### ADR-0102: Default Cursor-Based Pagination (ARC07-D14)
- **Context:** Offset-based pagination degrades severely on large datasets and produces duplicate or skipped records during live mutations.
- **Decision:** Collections use opaque, base64-encoded cursor pagination by default, with capped maximum page sizes.
- **Consequences:** High-performance index-backed pagination and stable collection traversal during concurrent inserts.

### ADR-0103: Optimistic Concurrency Control via ETags and Row Versions (ARC07-D15)
- **Context:** Concurrent visual menu edits risk silent data loss if updates overwrite without conflict detection.
- **Decision:** Stateful entities maintain row_version counters; mutating requests require If-Match or row_version verification.
- **Consequences:** Immediate detection of concurrent edits, returning 409 Conflict to protect editor state.

### ADR-0104: Idempotency Key Pattern for Mutation Retries (ARC07-D16)
- **Context:** Network interruptions during mutations cause duplicate creations or redundant charges on client retry.
- **Decision:** Critical mutating endpoints accept an Idempotency-Key header to cache and replay identical transaction responses.
- **Consequences:** Safe automated client retries with guaranteed once-and-only-once operational semantics.

### ADR-0105: Explicit Domain Contracts for Internal Module Communication (ARC07-D17)
- **Context:** Direct cross-module database joins inside the modular monolith erode domain boundaries and increase coupling.
- **Decision:** Modules interact strictly through explicit application service interfaces and published domain events.
- **Consequences:** Clean domain modularity, ease of testing with mock interfaces, and future microservice extraction viability.

### ADR-0106: Transactional Outbox for Reliable Event Dispatch (ARC07-D18)
- **Context:** Emitting external events without transactional guarantees risks event loss if the process crashes after DB commit.
- **Decision:** Domain events are written to the outbox_events table within the primary business transaction.
- **Consequences:** Guaranteed at-least-once event delivery to external listeners and webhooks.

### ADR-0107: Provider Adapter Pattern for External Services (ARC07-D19)
- **Context:** Direct coupling to external vendor SDKs (SendGrid, AWS S3, Stripe) prevents local testing and limits portability.
- **Decision:** External dependencies are abstracted behind abstract service protocols with pluggable provider adapters.
- **Consequences:** Painless local development with in-memory/console mocks and zero vendor lock-in.

### ADR-0108: Cryptographically Signed Webhook Delivery with Replay Defense (ARC07-D20)
- **Context:** Webhooks delivered over the public internet can be intercepted, forged, or replayed.
- **Decision:** Webhook payloads are signed with HMAC-SHA256, include timestamp headers, and require signature verification.
- **Consequences:** Guaranteed payload authenticity, tamper prevention, and complete defense against replay attacks.

### ADR-0109: Decoupled Public Menu Read Model (ARC07-D21)
- **Context:** High-volume public QR menu browsing must not put read contention on transactional draft menu tables.
- **Decision:** Public menu endpoints serve immutable published snapshots without tenant authentication overhead.
- **Consequences:** Sub-millisecond response times, edge CDN cacheability, and zero draft leakage to public consumers.

### ADR-0110: Tiered Rate Limiting by Endpoint Class (ARC07-D22)
- **Context:** Uniform rate limits either throttle legitimate interactive users or fail to protect against DDoS attacks.
- **Decision:** Rate limits are tiered by endpoint sensitivity: public diners (120/min), tenant users (600/min), auth (10/min).
- **Consequences:** Robust defense against brute force and DDoS attacks while maintaining a responsive user experience.

### ADR-0111: Correlation IDs and Structured Telemetry (ARC07-D23)
- **Context:** Debugging distributed request failures without request tracing is inefficient and prone to error.
- **Decision:** Every request receives an X-Request-ID preserved across logs, errors, and background outbox dispatchers.
- **Consequences:** Instant trace correlation across frontend clients, backend services, and external webhook logs.

### ADR-0112: TanStack Query for Frontend API State Management (ARC07-D24)
- **Context:** Uncoordinated client-side fetch calls cause redundant network traffic, stale data, and race conditions.
- **Decision:** Frontend network state is managed via TanStack Query with structured query keys and optimistic mutation updates.
- **Consequences:** Automated background refetching, intelligent cache invalidation, and reduced client network load.

### ADR-0113: 100% API Parity Between Managed SaaS and Customer-Hosted Editions (ARC07-D25)
- **Context:** Separate API implementations for cloud and self-hosted editions create maintenance overhead and feature drift.
- **Decision:** Both editions share identical FastAPI route declarations, schemas, validation rules, and error contracts.
- **Consequences:** Complete architectural parity; customer-hosted deployments receive all enterprise capabilities without code changes.

### ADR-0114: Configuration-Driven, Code-Free Customization Architecture (ARC08-D01)
- **Context:** Restaurant operators need to customize visual presentation without code forks, custom CSS files, or developer intervention.
- **Decision:** Customization is driven strictly by JSON configuration documents conforming to versioned schemas.
- **Consequences:** Safe, portable menu customization across cloud and self-hosted environments without code mutation.

### ADR-0115: Dual-Editor Parity Over Shared Customization Document (ARC08-D02)
- **Context:** Non-technical operators prefer form controls (Settings Editor), while designers prefer drag-and-drop (Visual Editor).
- **Decision:** Both editors operate directly on the exact same underlying JSON customization document with bi-directional synchronization.
- **Consequences:** Zero state bifurcation, immediate interoperability, and freedom for operators to switch modes mid-edit.

### ADR-0116: Strict Proscription of Arbitrary CSS and Executable Code (ARC08-D03)
- **Context:** Allowing user-supplied CSS strings or `<script>` tags creates critical XSS and UI spoofing attack vectors.
- **Decision:** Custom CSS strings, style injection, inline scripts, and javascript: URLs are strictly prohibited and rejected by the validator.
- **Consequences:** Immunity to stored XSS and presentation hijacking; guaranteed layout stability across all viewports.

### ADR-0117: Hierarchical Design Token Taxonomy (ARC08-D04)
- **Context:** Raw styling values scatter theme rules and break visual coherence across complex menu layouts.
- **Decision:** Styles are governed by a strictly typed token taxonomy (color, typography, spacing, radius, shadow, elevation).
- **Consequences:** Consistent visual rhythm, automated theme switching, and simplified multi-brand governance.

### ADR-0118: Canonical JSON Schema Validation for Documents (ARC08-D05)
- **Context:** Untyped JSON documents risk corrupting database storage and crashing frontend rendering components.
- **Decision:** Customization documents are strictly validated against draft-07/2020-12 JSON Schemas on every mutation.
- **Consequences:** Deterministic contract enforcement, structured client error diagnostics, and safe persistence.

### ADR-0119: Bounded Document Size and Complexity Limits (ARC08-D06)
- **Context:** Unbounded JSON payloads degrade memory, increase latency, and enable DoS attacks against backend parsers.
- **Decision:** Hard limits enforced: max 256 KB document size, max 100 component instances, max 10 levels of JSON nesting.
- **Consequences:** Guaranteed memory predictability, fast parsing under 5ms, and protection against resource exhaustion.

### ADR-0120: Platform Theme Catalogue and Baseline Presets (ARC08-D07)
- **Context:** Restaurants require professionally designed aesthetic starting points out of the box.
- **Decision:** The platform provides 6 immutable baseline themes (Luxury, Minimal, Rustic, Contemporary, Vibrant, Editorial).
- **Consequences:** Instant out-of-the-box utility, reduced design effort for restaurants, and consistent baseline quality.

### ADR-0121: Responsive Grid and Slot Layout Architecture (ARC08-D08)
- **Context:** Different restaurant types require distinct physical presentation patterns (e.g., drinks list vs visual food grid).
- **Decision:** 4 responsive layout structures provided (List, Grid, Image Cards, Editorial) with mobile/tablet/desktop breakpoints.
- **Consequences:** Seamless adaptation across smartphones, tablets, and desktop displays with zero horizontal overflow.

### ADR-0122: Strict Component Registry and Slot Compatibility (ARC08-D09)
- **Context:** Placing components into arbitrary layout regions breaks responsive flow and creates visual corruption.
- **Decision:** 13 registered components may only be mounted into their explicitly declared semantic slots.
- **Consequences:** Structural integrity guaranteed; impossible to mount invalid component hierarchies.

### ADR-0123: Component Prop Schema Validation (ARC08-D10)
- **Context:** Component instances require customization properties that must not break component rendering logic.
- **Decision:** Each registered component declares a strict JSON schema for its props; unknown properties are rejected.
- **Consequences:** Clean component runtime execution, zero runtime crashes from unexpected props, and self-documenting UI.

### ADR-0124: Deterministic Theme Resolution and Reset Semantics (ARC08-D11)
- **Context:** Merging tenant overrides with base theme presets must be reproducible across both backend and frontend.
- **Decision:** Theme resolution is an idempotent pure function using recursive deep-merge, where null values reset tokens.
- **Consequences:** Identical rendering in SSR, CSR, and headless exports; predictable reset behavior for operators.

### ADR-0125: Deterministic CSS Custom Property Emission (ARC08-D12)
- **Context:** Applying design tokens efficiently without heavy runtime CSS-in-JS libraries or style recompilation.
- **Decision:** Resolved tokens are converted directly into deterministic CSS custom properties under the --mm- namespace.
- **Consequences:** Zero runtime JavaScript styling overhead, native browser performance, and instantaneous theme swaps.

### ADR-0126: Scoped CSS Variable Injection Container (ThemeScope) (ARC08-D13)
- **Context:** Injected CSS variables on the root document can leak across dashboard views and break admin controls.
- **Decision:** CSS custom properties are scoped strictly to a wrapper container (ThemeScope) enclosing the menu preview/canvas.
- **Consequences:** Complete style isolation between host application and tenant menu preview.

### ADR-0127: Optimistic Concurrency Control via If-Match Revision Tokens (ARC08-D14)
- **Context:** Multiple restaurant staff members editing the same menu draft concurrently cause lost updates.
- **Decision:** Mutating requests require an If-Match header matching the current revision; mismatches return HTTP 409 Conflict.
- **Consequences:** Complete elimination of silent lost updates; explicit conflict detection surfaces to users.

### ADR-0128: Immutable Revision History and Restoration Semantics (ARC08-D15)
- **Context:** Operators make mistakes during menu editing and require full version tracking and rollback capabilities.
- **Decision:** Every successful draft save creates an immutable CustomizationRevision record; restorations append new revisions.
- **Consequences:** Complete auditability, reversible changes, and non-destructive version rollback.

### ADR-0129: Ephemeral Preview Generation Architecture (ARC08-D16)
- **Context:** Operators need to preview unsaved theme tweaks without committing changes or polluting revision logs.
- **Decision:** The /preview endpoint computes and returns resolved styles in-memory without touching database storage.
- **Consequences:** Rapid visual feedback, zero database write amplification, and clean revision logs.

### ADR-0130: Published Menu Snapshot Decoupling (ARC-09/ARC-10) (ARC08-D17)
- **Context:** Draft customization changes made by operators must never immediately impact public diner menus.
- **Decision:** Publication creates an immutable frozen snapshot; public diners read exclusively from published releases.
- **Consequences:** Zero read contention on draft tables, stable diner experiences, and atomic release workflows.

### ADR-0131: Strict Multi-Tenant Customization Isolation (ARC08-D18)
- **Context:** In shared SaaS deployments, tenant customization data must be completely inaccessible to other tenants.
- **Decision:** All customization queries join Restaurant and enforce Restaurant.organization_id == tenant.organization_id.
- **Consequences:** Absolute tenant isolation meeting P0 security requirements; zero cross-tenant visibility.

### ADR-0132: Cross-Tenant Security Denial via HTTP 404/403 (ARC08-D19)
- **Context:** Returning 403 on non-owned resources allows attackers to enumerate the existence of other tenants' menus.
- **Decision:** Cross-tenant resource lookups return HTTP 404 Not Found, treating unauthorized resources as non-existent.
- **Consequences:** Prevention of resource enumeration attacks and uniform tenant-scoped error handling.

### ADR-0133: Dual Implementation Parity (Python & TypeScript) (ARC08-D20)
- **Context:** Theme resolution is required in both the Python backend (API previews) and TypeScript frontend (live editor).
- **Decision:** Python and TypeScript resolvers use identical deep-merge algorithms and pass the same test fixtures.
- **Consequences:** Guaranteed pixel-identical rendering between client-side visual editor and server-rendered previews.

### ADR-0134: Bounded Undo/Redo History via Command Pattern (ARC08-D21)
- **Context:** Unbounded in-memory editor undo stacks consume excessive browser memory and cause tab crashes.
- **Decision:** Editor history is bounded to 50 states using an immutable command pattern stack.
- **Consequences:** Safe, predictable memory footprint with full undo/redo functionality for operator workflows.

### ADR-0135: Multi-Viewport Canvas Preview Architecture (ARC08-D22)
- **Context:** Restaurant menus are browsed across diverse mobile, tablet, and desktop devices.
- **Decision:** The visual editor incorporates a multi-viewport preview container simulating 375px, 768px, and 1280px widths.
- **Consequences:** Operators can verify mobile responsiveness directly in the editor before publishing.

### ADR-0136: WCAG 2.1 AA Color Contrast Enforcement (ARC08-D23)
- **Context:** Low contrast text in digital menus creates accessibility barriers for visually impaired diners.
- **Decision:** Platform themes and token combinations are tested to guarantee a minimum 4.5:1 text-to-surface contrast ratio.
- **Consequences:** Compliance with international accessibility standards and effortless readability for all diners.

### ADR-0137: Zero Runtime Database Lookups for Public Menu Themes (ARC08-D24)
- **Context:** Millions of public diner requests querying database themes would degrade database throughput.
- **Decision:** Public menu rendering consumes statically pre-resolved token snapshots from CDN edge caches.
- **Consequences:** Sub-millisecond TTFB, massive scalability under peak dining hours, and zero database strain.

### ADR-0138: File Manifest Resiliency with In-Memory Caching (ARC08-D25)
- **Context:** Redis outages or transient cache failures must never disrupt platform theme and component catalogues.
- **Decision:** Registries load from local JSON manifest files on startup and cache definitions in process memory.
- **Consequences:** 100% platform availability even during external cache service degradation.

### ADR-0139: Automated 104-Test Scenario Architecture Matrix (ARC08-D26)
- **Context:** Complex token and layout rules require exhaustive automated regression protection.
- **Decision:** An automated 104-scenario test catalogue (ARC08-T001 to T104) is implemented and enforced in CI/CD.
- **Consequences:** Zero undetected regression bugs, comprehensive specification coverage, and guaranteed stability.

### ADR-0140: Complete 28-Document Architectural Documentation Baseline (ARC08-D27)
- **Context:** Large-scale engineering requires authoritative, unambiguous architecture documentation.
- **Decision:** Author and maintain the complete 28-document ARC-08 architecture documentation suite in docs/architecture/.
- **Consequences:** Complete architectural transparency, rapid developer onboarding, and long-term maintainability.


### ADR-0141: Pure Presentation Engine Decoupled From Persistence (ARC09-D01)
- **Context:** High-concurrency menu delivery must scale horizontally without database bottlenecks.
- **Decision:** The core rendering engine (@modularmenu/menu-renderer) is engineered as a pure function with zero database or network dependencies.
- **Consequences:** Deterministic output, trivial unit testability, and edge-deployable presentation logic.

### ADR-0142: Strict DTO Separation for Public Delivery vs Draft Preview (ARC09-D02)
- **Context:** Anonymous public menu consumers must never receive unapproved dishes or internal tenant identifiers.
- **Decision:** Maintain separate, strictly typed DTO models (PublicMenuRenderResponse vs DraftPreviewResponse) with distinct schemas.
- **Consequences:** Impossible for draft edits or sensitive billing/membership metadata to leak to dining guests.

### ADR-0143: Immutable Published Snapshots as Exclusive Source of Truth (ARC09-D03)
- **Context:** Live database entity queries during menu browsing create transactional contention and inconsistent states.
- **Decision:** Public menu delivery reads exclusively from immutable published snapshots in MenuVersion.
- **Consequences:** Sub-10ms response times, snapshot-level immutability, and zero write lock contention.

### ADR-0144: Deterministic SHA-256 Checksum Computation for ETags (ARC09-D04)
- **Context:** Cache invalidation across global CDNs requires stable, cryptographic content signatures.
- **Decision:** Compute deterministic SHA-256 hashes of canonical serialized snapshot dictionaries and map them directly to HTTP ETags.
- **Consequences:** Exact content verification, tamper detection, and deterministic CDN cache invalidation.

### ADR-0145: Standardized HTTP 304 Conditional GET Handling (ARC09-D05)
- **Context:** Repeated QR code scans during dinner service should minimize data transfer and cellular latency.
- **Decision:** Implement RFC 7232 If-None-Match conditional GET support returning HTTP 304 Not Modified without response bodies.
- **Consequences:** Massive bandwidth savings, sub-5ms roundtrips, and zero cellular overhead for returning diners.

### ADR-0146: Server-Side Rendering (SSR) via Next.js App Router (ARC09-D06)
- **Context:** Public digital menus must be indexed by search engines and render instantly on low-powered mobile devices.
- **Decision:** Use Next.js dynamic App Router routes (/r/[slug]/[menuSlug]) with server-side rendering and dynamic SEO metadata.
- **Consequences:** Maximum SEO discoverability, zero client-side hydration delay, and rich OpenGraph social sharing previews.

### ADR-0147: Five Mandatory Structural Presentation Slots (ARC09-D07)
- **Context:** Layout flexibility must not compromise structural coherence across diverse restaurant menus.
- **Decision:** Enforce five mandatory layout slots: header, navigation, category_section, item_card, and footer.
- **Consequences:** Predictable component composition while allowing unlimited visual component swappability.

### ADR-0148: Controlled Component Registry with Rejection on Unknowns (ARC09-D08)
- **Context:** Malformed layout payloads could attempt to load unregistered or arbitrary components.
- **Decision:** Enforce a whitelist catalogue (REGISTERED_RENDER_COMPONENTS) and raise RenderComponentNotFoundError on unrecognized names.
- **Consequences:** Security against injection and guaranteed component contract adherence.

### ADR-0149: Safe Fallback Component Hierarchy for Missing Widgets (ARC09-D09)
- **Context:** Deprecated components or partial layout configurations must not cause white-screen rendering failures.
- **Decision:** Apply a fallback resolution hierarchy defaulting to standard hero headers, pill navigation, and item cards.
- **Consequences:** Maximum resilience and backwards compatibility for legacy menus.

### ADR-0150: Scoped CSS Design Tokens via ThemeScope Container (ARC09-D10)
- **Context:** Restaurant styling customizations must not pollute global frontend dashboard styles.
- **Decision:** Inject CSS custom properties within a scoped .theme-scope-container DOM boundary.
- **Consequences:** Total style isolation, instant theme switching, and zero stylesheet bleed.

### ADR-0151: Strict Prohibition of Raw User CSS Code Injection (ARC09-D11)
- **Context:** Allowing free-form CSS text enables cross-site scripting (XSS) and phishing attacks.
- **Decision:** Restrict restaurant customizations exclusively to structured design token values validated against hex color patterns.
- **Consequences:** Absolute immunity against CSS-based data exfiltration and visual hijacking.

### ADR-0152: High-Visibility Visual Watermarking on Draft Previews (ARC09-D12)
- **Context:** Operators inspecting draft menus must never mistake an unapproved draft for a live public menu.
- **Decision:** Affix a prominent top banner and watermark text ("PREVIEW MODE — Unpublished Draft") on preview pages.
- **Consequences:** Zero operational confusion and distinct visual assurance.

### ADR-0153: Private No-Store Cache-Control Headers for Previews (ARC09-D13)
- **Context:** Operator preview endpoints must never be cached by intermediate proxies or shared CDNs.
- **Decision:** Return Cache-Control: private, no-cache, no-store, must-revalidate on all draft preview responses.
- **Consequences:** Real-time visibility into draft changes without stale proxy pollution.

### ADR-0154: Exact Decimal Arithmetic for Monetary Values (ARC09-D14)
- **Context:** Floating point rounding errors in prices lead to compliance and billing discrepancies.
- **Decision:** Store and validate prices using exact Decimal representation, strictly enforcing non-negativity (price >= 0.00).
- **Consequences:** Financial accuracy, multi-currency compliance, and zero rounding artifacts.

### ADR-0155: Standard Currency Symbol Display Based on Profile (ARC09-D15)
- **Context:** Global restaurant menus require native currency representation (€, $, £, ₹).
- **Decision:** Resolve currency symbols from the restaurant profile currency, formatting fractional and integer amounts cleanly.
- **Consequences:** Native localized diner experience across domestic and international markets.

### ADR-0156: Out-of-Stock Item Presentation Policy Support (ARC09-D16)
- **Context:** Different restaurant operations prefer either hiding sold-out dishes or showing them greyed out.
- **Decision:** The rendering engine supports both out-of-stock policies (hide item vs display disabled with aria-disabled="true").
- **Consequences:** Operational flexibility for kitchens and clear communication to dining guests.

### ADR-0157: Standardized Dietary Badges and Spice Normalization (ARC09-D17)
- **Context:** Guests with dietary restrictions require immediate, unmistakable visual cues.
- **Decision:** Normalize dietary tags (Veg, Non-Veg, Vegan, Jain, Egg) and spice ratings into standardized presentation badges.
- **Consequences:** Dietary transparency, reduced server ordering questions, and guest dietary safety.

### ADR-0158: Responsive Breakpoint Architecture for All Form Factors (ARC09-D18)
- **Context:** Menus are viewed on small smartphones, large tablets, and desktop displays.
- **Decision:** Implement standardized responsive breakpoints (mobile: 0-639px, tablet: 640-1023px, desktop: 1024px+).
- **Consequences:** Flawless mobile rendering with expanded grid density on tablets and desktops.

### ADR-0159: Strict 120 kB First Load JavaScript Bundle Ceiling (ARC09-D19)
- **Context:** Poor mobile cellular coverage in basement restaurants demands ultra-lightweight bundles.
- **Decision:** Maintain public menu first load JS under 120 kB (achieved 92.0 kB).
- **Consequences:** Sub-second time-to-interactive even on congested 3G/4G dining networks.

### ADR-0160: Fixed Aspect Ratio Containers to Prevent CLS (ARC09-D20)
- **Context:** Images loading asynchronously can push menu content down, creating disruptive Cumulative Layout Shift.
- **Decision:** Enforce fixed aspect ratio containers (16:9, 1:1) for all dish and cover images.
- **Consequences:** Zero visual jumping, smooth scrolling, and perfect Core Web Vitals score.

### ADR-0161: Priority Image Preloading for Hero Covers (ARC09-D21)
- **Context:** Restaurant brand cover photos represent the primary visual element above the fold.
- **Decision:** Mark restaurant cover images with priority preloading while lazy-loading item photos below the fold.
- **Consequences:** Optimal Largest Contentful Paint (LCP) and minimized bandwidth consumption.

### ADR-0162: Mandatory Screen Reader Alt Text Generation (ARC09-D22)
- **Context:** Visually impaired diners using screen readers need descriptive descriptions of dish photos.
- **Decision:** Automatically generate descriptive alt text ("Photo of {dish_name}") on all rendered food imagery.
- **Consequences:** Full screen reader accessibility without requiring tedious manual operator alt text entry.

### ADR-0163: WCAG 2.1 AA 4.5:1 Contrast Ratio Enforcement (ARC09-D23)
- **Context:** Dim restaurant dining lighting exacerbates readability challenges for low-contrast digital menus.
- **Decision:** Validate all theme presets and custom token pairs to guarantee >= 4.5:1 contrast against surface backgrounds.
- **Consequences:** Effortless readability in dim dining room environments.

### ADR-0164: Minimum 44x44px Touch Target Size (ARC09-D24)
- **Context:** Diners scrolling on mobile phones frequently mis-tap undersized navigation pills or buttons.
- **Decision:** Enforce 44x44px minimum interactive bounding boxes across all clickable elements.
- **Consequences:** Comfortable, frustration-free touch interactions for diners of all ages.

### ADR-0165: Stateless Pure Function Execution for Concurrency (ARC09-D25)
- **Context:** Peak dining rushes generate bursts of hundreds of concurrent menu views.
- **Decision:** Eliminate all shared process state and write transactions in the rendering path.
- **Consequences:** Linear horizontal scalability and complete concurrency safety.

### ADR-0166: React Error Boundary Isolation for Resilient Rendering (ARC09-D26)
- **Context:** A single corrupt dish item or failed component must never crash the entire restaurant menu.
- **Decision:** Enclose rendering blocks within MenuRenderErrorBoundary to isolate localized failures.
- **Consequences:** High availability and graceful degradation in production.

### ADR-0167: Automated 120-Test Catalogue for Full Verification (ARC09-D27)
- **Context:** The complexity of menu rendering demands exhaustive automated regression coverage.
- **Decision:** Implement and enforce a comprehensive 120-scenario automated test suite (ARC09-T001 to ARC09-T120).
- **Consequences:** 100% verified compliance across normalization, layouts, components, pricing, caching, accessibility, and performance.

### ADR-0168: Immutable Snapshot Publication Model (ARC10-D01)
- **Context:** Mutable live database states risk serving partially configured or inconsistent menus to dining guests.
- **Decision:** Every successful publication constructs an immutable snapshot containing all menu and presentation configurations.
- **Consequences:** Tamper-proof historical records, predictable public rendering, and complete decoupling from ongoing draft edits.

### ADR-0169: Immutable Saved Draft Revision History (ARC10-D02)
- **Context:** Unsaved or unversioned draft changes make conflict resolution impossible during collaborative editing.
- **Decision:** Saved draft edits create immutable DraftRevision records with monotonic numbers and parent pointers.
- **Consequences:** Traceable editing history, reversible draft state, and foundation for optimistic concurrency control.

### ADR-0170: Monotonic Integer Version Numbering per Menu (ARC10-D03)
- **Context:** Random UUIDs or timestamp versions are difficult for human restaurant operators to discuss and audit.
- **Decision:** Publications receive sequentially increasing positive integers starting at 1 per menu.
- **Consequences:** Clear, unambiguous version identities (v1, v2, v3) for restaurant teams and support staff.

### ADR-0171: Non-Destructive Rollback via Historical Snapshot Reactivation (ARC10-D04)
- **Context:** Rollbacks that overwrite or delete intermediate publications destroy historical audit trails.
- **Decision:** Rollback shifts the active publication pointer to an existing historical snapshot without mutating history.
- **Consequences:** Total audit preservation; previous states remain fully inspectable and subsequent edits increment version numbers normally.

### ADR-0172: Single Authoritative Active Publication Pointer Table (ARC10-D05)
- **Context:** Boolean is_current flags scattered across publication records can desynchronize and create split-brain activations.
- **Decision:** Maintain a dedicated menu_active_publications table with a primary key on (organization_id, menu_id).
- **Consequences:** Physically guaranteed at-most-one active publication per menu at the database constraint level.

### ADR-0173: PostgreSQL Database Transaction as Commit Boundary (ARC10-D06)
- **Context:** Partial publication commits (e.g. snapshot saved but active pointer not updated) leave the system in an invalid state.
- **Decision:** Snapshot insert, publication metadata, active pointer update, activation history, and outbox event commit within a single ACID transaction.
- **Consequences:** Atomic all-or-nothing publication semantics; zero corrupted or half-published menus.

### ADR-0174: Optimistic Concurrency via If-Match Revision Checking (ARC10-D07)
- **Context:** Simultaneous publishes from multiple managers could overwrite concurrent changes silently.
- **Decision:** Publishing requires an If-Match header matching the current draft revision; mismatches return HTTP 409 Conflict.
- **Consequences:** Complete elimination of silent lost updates; explicit conflict handling on the client.

### ADR-0175: Scoped Idempotency Key Architecture for Mutation Operations (ARC10-D08)
- **Context:** Network timeouts cause automated client retries that risk creating duplicate publication records.
- **Decision:** Scoped Idempotency-Key headers cache operation fingerprints and replay original results safely.
- **Consequences:** Safe retry semantics; impossible to trigger duplicate versions via network replay.

### ADR-0176: PostgreSQL JSONB for Frozen Snapshot Storage (ARC10-D09)
- **Context:** Storing complex nested menu hierarchies across dozens of normalized tables adds immense query overhead.
- **Decision:** Store the frozen public menu payload as a single structured JSONB document in menu_publication_snapshots.
- **Consequences:** Sub-millisecond snapshot retrieval, atomic storage, and portability across database backends.

### ADR-0177: Canonical SHA-256 Serialization for Snapshot Integrity (ARC10-D10)
- **Context:** Snapshot payloads must be verified for tamper detection and deterministic cache tagging.
- **Decision:** Serialize snapshot dictionaries using key-sorted, compact JSON and calculate SHA-256 digests.
- **Consequences:** Cryptographically verified snapshot integrity and deterministic ETag generation.

### ADR-0178: Pinned Theme, Layout, and Component Versions in Snapshots (ARC10-D11)
- **Context:** Future updates to themes or component registries could unintentionally alter the look of older published menus.
- **Decision:** Snapshots explicitly pin theme_version, layout_version, and renderer_contract_version.
- **Consequences:** Guaranteed visual reproducibility across months or years of historical snapshots.

### ADR-0179: Strict Public Field Allowlist for Snapshot Construction (ARC10-D12)
- **Context:** A denylist approach to filtering snapshot data risks accidentally leaking new private fields added in the future.
- **Decision:** The snapshot builder copies only fields explicitly permitted by a strict public allowlist.
- **Consequences:** Defense-in-depth prevention of internal notes, billing tokens, passwords, or soft-delete flags reaching diners.

### ADR-0180: Revision-Bound Publication Readiness Validation Engine (ARC10-D13)
- **Context:** Validating a draft does not guarantee readiness if an editor edits dishes before hitting publish.
- **Decision:** Publication validation binds strictly to a specific draft_revision and content_hash, rechecked at publish time.
- **Consequences:** Impossible for stale validation certificates to authorize changed or corrupted draft content.

### ADR-0181: Transactional Outbox Pattern for Lifecycle Events (ARC10-D14)
- **Context:** Asynchronous publishing notifications or cache purges could be lost if the server process crashes after commit.
- **Decision:** Write lifecycle events (MenuPublished, MenuRolledBack) directly to outbox_events in the same database transaction.
- **Consequences:** Guaranteed at-least-once event delivery, zero dual-write vulnerabilities, and reliable asynchronous processing.

### ADR-0182: At-Least-Once Event Delivery with Idempotent Consumer Handling (ARC10-D15)
- **Context:** Distributed workers processing outbox queues can crash or retry, causing duplicate event deliveries.
- **Decision:** Event consumers track processed event IDs and execute side effects (cache purges) idempotently.
- **Consequences:** Safe horizontal worker scaling without duplicate side effects or corrupted cache states.

### ADR-0183: Version-Addressed Cache Keys and Edge Tag Invalidation (ARC10-D16)
- **Context:** Purging CDN caches by URL alone can be slow or subject to propagation lag.
- **Decision:** Internal caches use version-addressed keys (public-menu:rest:menu:pubId) and broadcast edge cache tag purges.
- **Consequences:** Instantaneous cache updates upon publication and zero stale content delivery.

### ADR-0184: Decoupled ARC-09 Renderer Integration via Active Pointer (ARC10-D17)
- **Context:** ARC-09 presentation composition must consume published data without coupling to publishing business logic.
- **Decision:** Public renderer resolves the active publication snapshot directly without draft dependencies.
- **Consequences:** Clean separation of concerns between publishing orchestration and public presentation rendering.

### ADR-0185: Centralized Role-Based Access Control for Publishing (ARC10-D18)
- **Context:** Menu publishing is a high-visibility business action that must be restricted to authorized restaurant roles.
- **Decision:** Enforce menu.publish and menu.rollback permissions, restricted to RestaurantOwner and RestaurantManager.
- **Consequences:** Prevents unauthorized junior staff from modifying public menu releases.

### ADR-0186: Durable Publication and Rollback Activation Ledger (ARC10-D19)
- **Context:** Restaurant operators need an unambiguous audit trail of who published or rolled back each menu version and why.
- **Decision:** All activation shifts are immutably logged in publication_activations with actor_id, reason, and timestamp.
- **Consequences:** Total operational transparency, accountability, and dispute resolution evidence.

### ADR-0187: Timezone-Aware UTC Scheduled Publications (P1) (ARC10-D20)
- **Context:** Restaurants operate in localized time zones; daylight savings and offset shifts cause missed launches.
- **Decision:** Schedules store canonical UTC instants along with localized timezone names and revalidate candidate state before firing.
- **Consequences:** Accurate automated menu switches (e.g. breakfast to lunch) across global time zones.

### ADR-0188: Revision-Bound Managerial Approval Workflow (P1) (ARC10-D21)
- **Context:** Enterprise restaurant chains require head chef or GM sign-off before menu prices change publicly.
- **Decision:** Approval records bind strictly to exact candidate draft revisions and SHA-256 hashes.
- **Consequences:** Prevents bait-and-switch modifications where an approved menu is subtly altered before publishing.

### ADR-0189: Unified SaaS and Customer-Hosted Publishing Core (ARC10-D22)
- **Context:** Maintaining divergent publishing logic for cloud SaaS and on-premise deployments increases defects.
- **Decision:** Share 100% of the Python publishing domain and application services across both editions.
- **Consequences:** Complete feature parity and single-codebase maintenance across all customer editions.

### ADR-0190: Non-Destructive Reconciliation Worker Architecture (ARC10-D23)
- **Context:** Transient database disconnects or interrupted worker jobs could leave operations in non-terminal states.
- **Decision:** The reconciliation engine audits publication state and outbox backlogs without ever rewriting historical records.
- **Consequences:** Self-healing operations, zero silent data corruption, and immediate operator visibility.

### ADR-0191: 3-Year Historical Publication Retention Policy (ARC10-D24)
- **Context:** Indefinite snapshot retention increases database storage footprint over many years of daily menu edits.
- **Decision:** Active publications are permanent; historical publications and audit logs are retained for a minimum of 3 years.
- **Consequences:** Full legal and regulatory compliance balance with predictable database storage scaling.



### ADR-0192: Docker Compose v2 as Primary Orchestration Engine (ARC11-D01)
- **Context:** Premature Kubernetes adoption introduces operational complexity, etcd quorum management overhead, and resource penalties for small restaurant appliances.
- **Decision:** Standardize on Docker Compose v2 profiles across development, staging, SaaS production, and customer-hosted installations.
- **Consequences:** Reproducible, lightweight container orchestration with zero vendor lock-in.

### ADR-0193: Unified Multi-Stage Container Images for SaaS & Customer-Hosted (ARC11-D02)
- **Context:** Divergent builds for cloud and customer-hosted editions cause test divergence and bug leakage.
- **Decision:** Build and publish identical container images; operational differences are controlled solely via environment variables and Compose overrides.
- **Consequences:** Single image artifact stream, 100% test fidelity, and simplified release maintenance.

### ADR-0194: Unprivileged Non-Root Execution across All Containers (ARC11-D03)
- **Context:** Running containers as root creates severe privilege escalation and container breakout risks.
- **Decision:** Mandate non-root user execution: `menuapp:menuapp` (UID/GID 10001) for Python services and `nextjs:nodejs` (UID/GID 1001) for frontend.
- **Consequences:** Eliminates root execution privileges; aligns with CIS Docker benchmarks.

### ADR-0195: Read-Only Root Filesystem with Ephemeral tmpfs Mounts (ARC11-D04)
- **Context:** Writable container root filesystems allow unauthorized modifications, persistence of malware, and non-deterministic state.
- **Decision:** Enforce `read_only: true` on production containers with explicit tmpfs mounts on `/tmp`.
- **Consequences:** Immutable runtime environments; unauthorized runtime mutations are physically prevented.

### ADR-0196: Strictly Ephemeral Redis with Graceful In-Memory Degradation (ARC11-D05)
- **Context:** Hard dependencies on Redis cause entire platform outages when cache clusters experience maintenance or failure.
- **Decision:** Redis is strictly non-authoritative; core read and write flows must seamlessly degrade to in-memory bypasses if Redis is offline.
- **Consequences:** Platform resilience is maintained; restaurants can continue taking orders even during Redis outages.

### ADR-0197: Expand-and-Contract Zero-Downtime Database Migration Protocol (ARC11-D06)
- **Context:** Destructive or blocking database migrations cause customer downtime and failed requests during deployments.
- **Decision:** Mandate expand-and-contract migrations where database changes remain forward and backward compatible across rolling releases.
- **Consequences:** Zero-downtime deployments without table locks or transaction aborts.

### ADR-0198: HMAC SHA-256 Signed URLs for Local Filesystem Object Storage (ARC11-D07)
- **Context:** Customer-hosted editions use local storage but must prevent unauthenticated enumeration or hotlinking of private restaurant media.
- **Decision:** Generate expiring, tamper-evident URLs protected by SHA-256 HMAC tokens for all local media access.
- **Consequences:** Parity with S3 pre-signed URLs without requiring complex third-party storage daemons.

### ADR-0199: Explicit TenantJobContext Envelope Required for Worker Jobs (ARC11-D08)
- **Context:** Asynchronous background jobs could execute without tenant scoping, risking cross-tenant data leakage.
- **Decision:** Require all background worker jobs to be wrapped in an explicit `TenantJobContext(organization_id, actor_id)` envelope.
- **Consequences:** Strict multi-tenant isolation guarantees extended to asynchronous and background processing.

### ADR-0200: Mandatory Pre-Migration Database Snapshot and Verification (ARC11-D09)
- **Context:** Migration scripts can fail mid-execution due to data anomalies or network disconnects, leaving database schemas in corrupted states.
- **Decision:** Automated migration tooling must execute a verified `pg_dump` snapshot prior to applying any Alembic revision.
- **Consequences:** Guaranteed point-in-time recovery before any structural database mutation.

### ADR-0201: Triple Health Probe Model (/live, /ready, /startup) (ARC11-D10)
- **Context:** Conflating process liveness with dependency readiness leads orchestrators to restart healthy processes during downstream outages.
- **Decision:** Separate probes into `/health/live` (process responsiveness), `/health/ready` (dependency check), and `/health/startup` (initialization).
- **Consequences:** Accurate orchestration restarts, zero thundering-herd container crashes during database maintenance.

### ADR-0202: Strict Environment Preflight Validation via Pydantic Settings (ARC11-D11)
- **Context:** Misconfigured production settings (e.g., debug enabled, default secrets) lead to critical security vulnerabilities.
- **Decision:** Fail fast at container startup using Pydantic Settings validators that reject insecure production configurations.
- **Consequences:** Impossible to boot production containers with debug mode or insecure default passwords.

### ADR-0203: Automated Secret Redaction in Logs, Exceptions, and Dumps (ARC11-D12)
- **Context:** Sensitive credentials logged during exceptions or startup expose credentials to log aggregation pipelines.
- **Decision:** Implement custom `__repr__` and `__str__` masking on all credential models, replacing secrets with `***`.
- **Consequences:** Clean logs and zero credential leakage in monitoring platforms and error traces.

### ADR-0204: Next.js 14 Standalone Mode with < 120 kB First Load JS Budget (ARC11-D13)
- **Context:** Standard Next.js production deployments carry bulky `node_modules`, bloating container images and slowing mobile guests.
- **Decision:** Enable `output: "standalone"` in Next.js build and enforce < 120 kB first load JavaScript budget.
- **Consequences:** Container size reduced by 70%; sub-second menu loading for guests on mobile data.

### ADR-0205: Python 3.12 Slim Debian Bookworm Standardized Base Image (ARC11-D14)
- **Context:** Alpine Linux Python builds suffer from musl libc performance penalties, while full Debian images carry unnecessary utilities and CVEs.
- **Decision:** Standardize backend and worker base images on `python:3.12-slim-bookworm`.
- **Consequences:** High-performance glibc runtime, minimized vulnerability surface, fast build times.

### ADR-0206: Nginx Reverse Proxy for TLS 1.3 Termination and Rate Limiting (ARC11-D15)
- **Context:** Direct exposure of Python and Node servers creates security and DDoS risks.
- **Decision:** Route all external traffic through an Nginx reverse proxy enforcing TLS 1.3, rate limits, and security headers.
- **Consequences:** Hardened perimeter, protection against brute-force attacks, and single entry point.

### ADR-0207: Dropping All Linux Capabilities (`cap_drop: [ALL]`) in Production (ARC11-D16)
- **Context:** Default Linux container capabilities provide attack surfaces for kernel exploits.
- **Decision:** Drop all Linux capabilities in production Compose files, running with minimum necessary permissions.
- **Consequences:** Prevents root escalation inside containers even if code execution occurs.

### ADR-0208: Isolated Internal Bridge Networks for Data Persistence Layer (ARC11-D17)
- **Context:** Direct exposure of PostgreSQL or Redis to host interfaces risks unauthorized database connections.
- **Decision:** Restrict database and Redis containers to an internal `data-net` bridge with zero host port mappings in production.
- **Consequences:** Database is physically unreachable from the public internet.

### ADR-0209: Bounded Exponential Backoff and Dead-Letter Queue in Worker (ARC11-D18)
- **Context:** Poison-pill events can lock worker threads in continuous retry loops, exhausting resources.
- **Decision:** Worker applies exponential backoff capped at 60s; moves events failing 5 attempts to dead-letter queue.
- **Consequences:** Uninterrupted queue throughput and visibility into toxic events for operator remediation.

### ADR-0210: Path Traversal Normalization Guard in Local Storage Adapter (ARC11-D19)
- **Context:** Local storage adapters handling user-supplied paths can be manipulated via `../` directory traversal attacks.
- **Decision:** Enforce canonical path resolution and verify that resolved paths reside strictly within the configured root directory.
- **Consequences:** Absolute prevention of host filesystem read/write vulnerabilities.

### ADR-0211: Encrypted Off-Host Backup Storage with 1h RPO and 4h RTO (ARC11-D20)
- **Context:** Storing backups on the same host leaves systems vulnerable to complete host or disk loss.
- **Decision:** Backups are compressed, AES-256 encrypted, and replicated off-host to secondary cloud or remote locations.
- **Consequences:** Adherence to strict disaster recovery SLOs: 1-hour RPO and 4-hour RTO.

### ADR-0212: GitHub Actions Automated Quality Gates with 100% Test Pass Gate (ARC11-D21)
- **Context:** Allowing broken or untested commits onto main branches causes production regressions.
- **Decision:** Require all 738 automated platform tests and linters to pass before code can merge to `develop` or `main`.
- **Consequences:** Regression-free releases and zero-tolerance policy for broken quality gates.

### ADR-0213: Explicit Manual Approval Gate for Production SaaS Deployments (ARC11-D22)
- **Context:** Continuous deployment directly to production without oversight risks deploying unverified changes during peak restaurant hours.
- **Decision:** Production deployments require explicit manual approval from authorized engineering leads in GitHub Actions.
- **Consequences:** Controlled release timing and scheduled maintenance windows.

### ADR-0214: Turnkey Single-Command Customer Appliance Offline Installation (ARC11-D23)
- **Context:** Restaurant IT staff require friction-free installation without complex manual configurations.
- **Decision:** Provide an automated turnkey installation script (`install-customer-hosted.sh`) capable of operating offline.
- **Consequences:** Frictionless on-premise installation in under 10 minutes.

### ADR-0215: Bounded 10 MB Maximum File Size for Media Ingestion (ARC11-D24)
- **Context:** Unbounded media uploads exhaust disk space and bandwidth, enabling denial-of-service attacks.
- **Decision:** Enforce strict 10 MB upload limits across reverse proxy, backend API, and storage adapters.
- **Consequences:** Bounded storage consumption and predictable bandwidth utilization.

### ADR-0216: Sanitized Database Error Responses on Probe Failures (ARC11-D25)
- **Context:** Returning raw SQL exception traces in health endpoints leaks internal server topology and credentials.
- **Decision:** Sanitize all health probe failure payloads to emit generic degraded status messages.
- **Consequences:** Zero information disclosure through public health monitoring endpoints.

### ADR-0217: Transactional Outbox Queue Lag Growth Telemetry (ARC11-D26)
- **Context:** Silent worker stall allows outbox backlogs to grow unnoticed until operators report delayed publishing.
- **Decision:** Emit telemetry alerts when unprocessed outbox events exceed 500 records or lag by more than 5 minutes.
- **Consequences:** Proactive operational alerting before customer-facing impact occurs.

### ADR-0218: Minimum 20 GB Disk Space Preflight Enforcement (ARC11-D27)
- **Context:** Deploying to hosts with insufficient disk causes database write freezes and corruption.
- **Decision:** Installation and deployment scripts verify at least 20 GB free disk space prior to proceeding.
- **Consequences:** Elimination of disk exhaustion failures during container startup or migrations.

### ADR-0219: Automated 30-Day TLS Certificate Expiry Alerting (ARC11-D28)
- **Context:** Expired SSL certificates immediately break diner access to QR digital menus.
- **Decision:** Monitoring alerts fire when SSL certificates have fewer than 30 days remaining until expiration.
- **Consequences:** Sufficient lead time for automated or manual certificate renewal.

### ADR-0220: Semi-Annual Simulated Disaster Recovery Restore Drills (ARC11-D29)
- **Context:** Untested backups frequently fail during actual disasters due to corrupted files or missing credentials.
- **Decision:** Mandate semi-annual simulated disaster recovery drills executing full restore scripts.
- **Consequences:** Verified backup viability and trained operational incident teams.

### ADR-0221: Automated Release Verification Smoke Suite Post-Deployment (ARC11-D30)
- **Context:** Successful container startup does not guarantee that frontend UI, backend API, and database are collaborating properly.
- **Decision:** Run automated smoke tests immediately following deployments, validating health probes, API routes, and static assets.
- **Consequences:** Fast detection of release regressions and immediate trigger for rollback if smoke tests fail.

### ADR-0222: Argon2id for Password Storage Hashing (ARC12-D01)
- **Context:** Standard password hashing algorithms like bcrypt have fixed memory requirements, whereas Argon2id provides configurable memory, time, and parallelism hardness against modern GPU/ASIC cracking.
- **Decision:** Mandate Argon2id as the exclusive password hashing algorithm with memory cost >= 64 MB, time cost >= 3 iterations, and parallelism >= 4 threads.
- **Consequences:** Maximum resistance against offline dictionary and brute force attacks.

### ADR-0223: Cryptographic 256-bit CSPRNG Session Identifiers (ARC12-D02)
- **Context:** Weak session identifiers can be predicted or brute-forced by malicious actors.
- **Decision:** Generate session tokens using cryptographically secure pseudorandom numbers (256-bit entropy) and store only their SHA-256 hashes server-side.
- **Consequences:** Session token exposure in database breaches does not reveal the bearer secret.

### ADR-0224: Immediate Session Rotation on Privilege Elevation (ARC12-D03)
- **Context:** Session fixation attacks allow an adversary to pre-set a session identifier that persists after user authentication.
- **Decision:** Rotate session tokens immediately upon login, password reset, or role changes, revoking the previous identifier.
- **Consequences:** Total elimination of session fixation risks.

### ADR-0225: __Host- Cookie Prefixes in Production Environments (ARC12-D04)
- **Context:** Standard cookies can be overwritten by insecure subdomains or altered via non-root path paths.
- **Decision:** Enforce the `__Host-` cookie name prefix in production with `Secure`, `HttpOnly`, and `SameSite=Lax`.
- **Consequences:** Browser enforces origin integrity, preventing cross-subdomain cookie hijacking.

### ADR-0226: Centralized RBAC Permission Table Mapping (ARC12-D05)
- **Context:** Scattered role checks in API routes lead to inconsistent authorization boundaries and privilege escalation bugs.
- **Decision:** Implement a centralized role-to-permission mapping dictionary and enforce authorization via `require_permission` dependency.
- **Consequences:** Uniform, auditable access control policies across all API endpoints.

### ADR-0227: Organization-Scoped Tenant Context Resolution (ARC12-D06)
- **Context:** Client-supplied organization headers or query parameters cannot be trusted as authoritative proof of access.
- **Decision:** Resolve tenant context server-side from authenticated session membership records.
- **Consequences:** Guaranteed tenant isolation preventing cross-tenant access.

### ADR-0228: Force Row Level Security on Tenant Database Tables (ARC12-D07)
- **Context:** Application bugs or query omissions can leak tenant records if isolation depends solely on application code.
- **Decision:** Enable `FORCE ROW LEVEL SECURITY` on all tenant-owned tables in PostgreSQL.
- **Consequences:** Database engine enforces isolation invariants even if table owner or application bugs occur.

### ADR-0229: Non-Bypass Application Database Runtime Role (ARC12-D08)
- **Context:** Database roles possessing `BYPASSRLS` or superuser privileges bypass all RLS policies.
- **Decision:** The runtime application database role must explicitly NOT possess `BYPASSRLS` or superuser privileges.
- **Consequences:** Application connections cannot circumvent row-level security.

### ADR-0230: Dual-Layer Tenant Isolation Guardrails (App + DB) (ARC12-D09)
- **Context:** Single-layer isolation models fail completely if a single component suffers a vulnerability.
- **Decision:** Enforce defense-in-depth: Application queries filter by tenant context, and PostgreSQL RLS filters as an independent safety net.
- **Consequences:** Redundant isolation guarantees preventing data leakage.

### ADR-0231: Anti-CSRF Token Validation with Bearer Exemption (ARC12-D10)
- **Context:** Cookie-authenticated browser sessions are vulnerable to cross-site request forgery on unsafe HTTP verbs.
- **Decision:** Enforce anti-CSRF token verification on cookie session mutations, while exempting Bearer token API calls.
- **Consequences:** Robust CSRF defense without breaking API integrations.

### ADR-0232: Strict Content Security Policy (CSP) Rules (ARC12-D11)
- **Context:** Cross-site scripting vulnerabilities can execute malicious scripts if CSP headers are permissive.
- **Decision:** Enforce strict CSP rules disallowing `unsafe-eval` and `unsafe-inline` scripts.
- **Consequences:** Defense against stored, reflected, and DOM-based XSS attacks.

### ADR-0233: Automated Security Response Headers Standard (ARC12-D12)
- **Context:** Missing security headers expose clients to clickjacking, MIME sniffing, and downgrade attacks.
- **Decision:** Inject HSTS, X-Content-Type-Options, X-Frame-Options, and Referrer-Policy on all HTTP responses.
- **Consequences:** Automated hardening across all web and API responses.

### ADR-0234: SSRF Outbound Network Request Guard (ARC12-D13)
- **Context:** Outbound HTTP requests can be abused to probe internal networks or cloud metadata services (169.254.169.254).
- **Decision:** Validate all outbound destination URLs and reject private, loopback, and link-local IP addresses.
- **Consequences:** Neutralization of SSRF vulnerabilities.

### ADR-0235: Strict Media Magic Byte File Signature Verification (ARC12-D14)
- **Context:** Attackers disguise malicious executables or scripts with image extensions.
- **Decision:** Inspect both MIME headers and file magic bytes, allowing only genuine JPEG, PNG, and WebP payloads.
- **Consequences:** Prevention of executable upload attacks.

### ADR-0236: 25 Megapixel Limit for Decompression Bomb Defense (ARC12-D15)
- **Context:** Highly compressed images (decompression bombs) cause memory exhaustion and denial of service when decompressed.
- **Decision:** Reject any image with total pixels exceeding 25,000,000 prior to memory buffer decompression.
- **Consequences:** Protection against image processing memory exhaustion attacks.

### ADR-0237: Canonical Object Key Isolation for Tenant Media (ARC12-D16)
- **Context:** Poorly partitioned media storage paths risk cross-tenant file overwrites or unauthorized reads.
- **Decision:** Enforce canonical keys strictly prefixed with `organizations/{org_id}/restaurants/{rest_id}/`.
- **Consequences:** Strict multi-tenant namespace isolation across storage adapters.

### ADR-0238: Webhook HMAC SHA-256 Cryptographic Verification (ARC12-D17)
- **Context:** Forged webhook payloads can simulate payments or state updates from external services.
- **Decision:** Verify inbound webhooks using constant-time HMAC SHA-256 comparison against shared secrets.
- **Consequences:** Cryptographic certainty of webhook authenticity and integrity.

### ADR-0239: Webhook Timestamp Drift Tolerance Limit (300s) (ARC12-D18)
- **Context:** Replay attacks utilize captured legitimate webhook payloads outside their operational window.
- **Decision:** Reject webhook events with timestamps drifting more than 300 seconds from server clock.
- **Consequences:** Mitigation of stale and replayed webhook events.

### ADR-0240: Webhook Idempotency & Replay Attack Defense (ARC12-D19)
- **Context:** Network retransmissions or replay attempts cause duplicate business executions (e.g. double subscriptions).
- **Decision:** Track processed webhook event IDs with 24-hour expiration and enforce idempotent processing.
- **Consequences:** Duplicate webhook events are safely acknowledged without re-execution.

### ADR-0241: Immutable Append-Only Audit Logging Ledger (ARC12-D20)
- **Context:** Audit logs can be altered or erased by compromised administrative accounts if mutation is permitted.
- **Decision:** Implement append-only audit tables with no update or delete operations exposed in application interfaces.
- **Consequences:** Non-repudiation and tamper-evident administrative history.

### ADR-0242: Automated Regex Credential Masking in Logs and Traces (ARC12-D21)
- **Context:** Accidental logging of passwords, tokens, or authorization headers exposes secrets in log aggregation tools.
- **Decision:** Implement automated regex sanitization masking sensitive keywords with `***` across all logging sinks.
- **Consequences:** Prevention of credential leakage into log storage.

### ADR-0243: Non-Root Application Container Execution (UID 1001) (ARC12-D22)
- **Context:** Containers running as root risk host system takeover in the event of a container breakout vulnerability.
- **Decision:** Run all application containers under unprivileged non-root users (`appuser` UID 1001, node UID 1000).
- **Consequences:** Hardened isolation and mitigation of container breakout risks.

### ADR-0244: Dropped Linux Capabilities in Production Containers (ARC12-D23)
- **Context:** Unnecessary Linux kernel capabilities provide vectors for privilege escalation inside containers.
- **Decision:** Configure Compose production profiles with `cap_drop: [ALL]` and `security_opt: [no-new-privileges:true]`.
- **Consequences:** Drastically reduced attack surface within runtime environments.

### ADR-0245: Isolated Internal Bridge Networks for Data Stores (ARC12-D24)
- **Context:** Database and cache ports exposed to public host interfaces risk unauthorized access.
- **Decision:** Place PostgreSQL and Redis on internal bridge networks with no host port bindings.
- **Consequences:** Data stores accessible exclusively to authenticated application backend containers.

### ADR-0246: Multi-Tier Token Bucket Rate Limiting (ARC12-D25)
- **Context:** API endpoints without rate limiting are susceptible to denial of service and brute force credential guessing.
- **Decision:** Enforce token bucket rate limits in Redis with automatic fallback to local memory counters.
- **Consequences:** Predictable API performance and protection against volumetric abuse.

### ADR-0247: Public Menu Immutable Pre-Rendered CDN Snapshot Caching (ARC12-D26)
- **Context:** Guest menu visits surge during dining hours and must not overload database compute capacity.
- **Decision:** Serve published menus as immutable pre-rendered snapshots via CDN edge caches with ETags and Stale-While-Revalidate.
- **Consequences:** Sub-300ms p95 latency for public menu consumers with near-zero database load.

### ADR-0248: Frontend 120 kB Gzip Initial JavaScript Budget (ARC12-D27)
- **Context:** Heavy JavaScript bundles degrade mobile diner experience on spotty cellular connections.
- **Decision:** Enforce a strict 120 kB gzip budget on initial client-side JavaScript for guest menu viewers.
- **Consequences:** Instant mobile load times and high Core Web Vitals performance scores.

### ADR-0249: Database Connection Pool Boundaries (20 Pool, 10 Overflow) (ARC12-D28)
- **Context:** Unconstrained database connection pooling exhausts PostgreSQL memory and leads to query queuing.
- **Decision:** Constrain asyncpg connection pools to `pool_size=20, max_overflow=10, pool_recycle=1800`.
- **Consequences:** Predictable database resource utilization and prevention of connection starvation.

### ADR-0250: Composite Indexing on Multi-Tenant Database Columns (ARC12-D29)
- **Context:** Multi-tenant queries filtering by restaurant and organization require rapid index lookups.
- **Decision:** Index tenant tables with composite keys starting with `organization_id, restaurant_id`.
- **Consequences:** O(log N) index scan efficiency and prevention of full table scans.

### ADR-0251: Transactional Outbox Pattern for Durable Asynchronous Events (ARC12-D30)
- **Context:** Asynchronous event publishing can fail after database commit, causing data inconsistency across services.
- **Decision:** Write events to a PostgreSQL `outbox` table within the same transaction as business data mutations.
- **Consequences:** Guaranteed at-least-once event delivery and total consistency across failures.

### ADR-0252: Bounded Exponential Backoff with Full Uniform Jitter (ARC12-D31)
- **Context:** Synchronized retry intervals create thundering herd spikes when downstream services recover.
- **Decision:** Calculate retry delays using exponential backoff with full uniform jitter.
- **Consequences:** Smoothly distributed retry load protecting recovering services.

### ADR-0253: Poison Pill Dead-Letter Queue Quarantine after 8 Attempts (ARC12-D32)
- **Context:** Malformed or persistently failing events block background queues and burn compute cycles indefinitely.
- **Decision:** Automatically route events failing 8 consecutive attempts to `dead_letter` status with full diagnostic context.
- **Consequences:** Queue backlog continues processing while poison pills are safely quarantined for investigation.

### ADR-0254: Three-State Circuit Breakers for External Integrations (ARC12-D33)
- **Context:** Remote API outages (email, payment, cloud storage) cause thread exhaustion and application hangs.
- **Decision:** Wrap outbound integrations in three-state circuit breakers (Closed, Open, Half-Open).
- **Consequences:** Fast failure during remote outages, preserving application thread pool availability.

### ADR-0255: Ephemeral Redis Resilient Graceful Degradation (ARC12-D34)
- **Context:** Total application failure caused by an optional cache or rate-limiting cluster is unacceptable.
- **Decision:** Treat Redis as ephemeral; automatically degrade to local in-memory sliding window counters and direct DB queries if Redis fails.
- **Consequences:** Core menu viewing and ordering workflows remain 100% available during Redis outages.

### ADR-0256: Disaster Recovery RPO <= 1h and RTO <= 4h Standards (ARC12-D35)
- **Context:** Catastrophic host or datacenter failure requires deterministic data recovery and service restoration guarantees.
- **Decision:** Implement continuous WAL archiving and automated off-host encrypted snapshots to ensure RPO <= 1h and RTO <= 4h.
- **Consequences:** Verifiable business continuity and resilience against catastrophic infrastructure loss.
