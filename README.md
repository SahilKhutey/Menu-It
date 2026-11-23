# Menu-It (ModularMenu™)

### Enterprise-Grade Configurable Multi-Tenant Digital Restaurant Menu Platform

[![Version](https://img.shields.io/badge/version-1.0.0--arc11-blue.svg?style=for-the-badge)](https://github.com/SahilKhutey/Menu-It/releases/tag/v1.0.0-arc11)
[![Architecture](https://img.shields.io/badge/Architecture-ARC--01%20to%20ARC--11%20Approved-success.svg?style=for-the-badge)](ARCHITECTURE.md)
[![Tests](https://img.shields.io/badge/Quality%20Gates-738%2F738%20Passing-brightgreen.svg?style=for-the-badge)](docs/tasklogs/README.md)
[![Devlogs](https://img.shields.io/badge/Devlogs-13%20Chronicles-orange.svg?style=for-the-badge)](docs/devlogs/README.md)
[![Tasklogs](https://img.shields.io/badge/Tasklogs-11%20Milestones-blueviolet.svg?style=for-the-badge)](docs/tasklogs/README.md)
[![Python](https://img.shields.io/badge/Python-3.12%20FastAPI-005571.svg?style=for-the-badge&logo=python)](backend/)
[![Next.js](https://img.shields.io/badge/Next.js-14%20App%20Router-black.svg?style=for-the-badge&logo=next.js)](frontend/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg?style=for-the-badge&logo=typescript)](frontend/)
[![License](https://img.shields.io/badge/License-Commercial%20Proprietary-red.svg?style=for-the-badge)](LICENSE)

---

## 🍽️ Overview

**Menu-It** (system identifier `ModularMenu`) is a high-performance, multi-tenant digital restaurant menu platform with a hybrid delivery model (**Managed Multi-Tenant Cloud SaaS** and **Customer-Hosted Dedicated Appliance**). Built **India-First** and **Web-First**, it empowers restaurants to craft, customize, version, and publish ultra-responsive digital dining experiences without engineering custom code forks or managing separate branches.

```
+----------------------------------------------------------------------------------------------------+
|                                    MENU-IT APPLICATION ECOSYSTEM                                   |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|   [ Table QR Code ] ──▶ [ Diner Mobile Webview ]          [ Visual Studio (3-Panel Editor) ]       |
|    - Sub-second LCP (<1.5s)   - Zero Login Friction         - Real-time CSS token preview (60fps)   |
|    - 95 kB JS bundle budget  - FSSAI Dietary Tags           - Category tree & dietary badge editor  |
|    - Dynamic QR Table Modal  - Instant Rollback             - Multi-branch brand governance         |
|                                     │                                      │                       |
|                                     ▼                                      ▼                       |
|                         [ Read Path (CQRS-Lite) ]              [ Write Path (Relational) ]         |
|                         - Immutable SHA-256 Snapshots          - SQLAlchemy 2.0 Async ORM          |
|                         - Zero DB Joins at table scan          - Strict `lazy="raise"` loading     |
|                         - Edge-Cacheable JSON Payload          - Fixed-precision Decimal Currency  |
|                                     │                                      │                       |
|                                     └──────────────────┬───────────────────┘                       |
|                                                        │                                           |
|                                                        ▼                                           |
|                                          [ FastAPI Application Core ]                              |
|                                          - Multi-tenant boundary middleware                        |
|                                          - RFC 7807 problem details error format                   |
|                                          - OpenAPI 3.1 contract generation                         |
|                                                        │                                           |
|                                                        ▼                                           |
|                                    [ PostgreSQL 16 + Row-Level Security ]                         |
|                                    - Multi-tenant shared relational database                       |
|                                    - WORM (Write-Once, Read-Many) menu_versions                    |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

## ✨ Key Platform Features

### 🎨 1. Configuration-Driven Theme & Layout Engine (Zero-Fork Invariant)

- **Zero Bespoke Code:** Visual styling (color palettes, typography pairings, spacing density, card styles) is 100% driven by JSON design token configurations validated via JSON Schema (`packages/contracts/theme_schema.json`).
- **6 Pre-Built Visual Presets:**
  - **Luxury:** Dark obsidian surface (`#0D0E12`), Cinzel serif typography, gold accents (`#D4AF37`), elevated card styling.
  - **Minimal:** Stark monochrome, ultra-clean Inter typography, high-contrast flat styling.
  - **Rustic:** Earthy terracotta hues (`#8B4513`, `#E6D5B8`), warm amber highlights, comfortable spacing.
  - **Vibrant:** Playful crimson & mango tones, rounded borders (`borderRadius: "lg"`), dynamic food photography.
  - **Contemporary:** Slate-charcoal palette, compact density, modern geometric sans typography.
  - **Editorial:** Serif headlines, spacious magazine-style layouts, elegant high-end tasting presentation.
- **Instant 60fps Preview:** Design tokens compile directly to CSS Custom Properties (`--theme-*`) on the preview container without expensive React DOM re-renders.

### 🛡️ 2. Defense-in-Depth Multi-Tenancy

- **Perimeter 1 (Ingress Gateway):** JWT session validation and bearer signature checks.
- **Perimeter 2 (Application Boundary):** `verify_restaurant_access` dependency ensures callers hold active administrative membership for the targeted tenant before any action.
- **Perimeter 3 (Kernel Persistence):** PostgreSQL Row-Level Security (RLS) policies prevent data leakage across restaurants coexisting within a shared database.

### ⚡ 3. CQRS-Lite Immutable Snapshot Publishing

- **Extreme Read/Write Asymmetry:** Dining guests scanning QR codes at tables demand instant load times. Administrative relational tables (`menus`, `categories`, `menu_items`) are separated from the public read path.
- **Atomic Compilation:** Publishing serializes active dishes, variants, allergens, theme tokens, and layouts into a frozen JSON snapshot stamped with a cryptographic **SHA-256 checksum** and incrementing version integer (`v1`, `v2`, ...).
- **Zero Relational Joins:** Public diners read pre-compiled snapshot payloads directly in <5ms.
- **Instant Rollback:** Reverting to a previous menu version merely updates the active publication pointer.

### 📱 4. Diner-First Mobile Ergonomics (India-First & Web-First)

- **Zero App Download & Zero Login:** Dining guests access the menu immediately upon scanning a table QR code.
- **Strict Mobile Bundle Budget:** Total First Load JavaScript is **95.2 kB** (well below the 120 kB ceiling).
- **FSSAI Dietary Classification:** High-contrast, standardized badges for **Veg** (green dot in green square), **Non-Veg** (red dot in red square), **Egg** (amber dot in amber square), **Vegan**, and **Jain**.
- **Allergen Matrix:** Clear warnings for Dairy, Gluten, Nuts, Soy, Crustaceans, and Shellfish.
- **Integrated Table QR Sharing:** On-the-fly QR code generation (`image/png`) for table card printing and instant diner sharing.

### 🐳 5. Dual-Model Binary Portability

- **Profile A (Managed Multi-Tenant Cloud SaaS):** Centralized cloud infrastructure managed for onboarded restaurants.
- **Profile B (Customer-Hosted Appliance):** Single-tenant / dedicated container appliance running on customer-owned on-premises servers.
- **Invariant:** Both profiles compile from the **identical codebase and container image**; deployment modes are activated via pluggable environment variable adapters.

---

## 🏛️ System Architecture Series

The engineering specifications of ModularMenu are formally documented in the 12-part architecture series located in [`documentation/03_System_Architecture/`](documentation/03_System_Architecture/):

| Architecture Doc | Title                                                                                                                                | Status                     | Scope                                                                                                              |
| :--------------- | :----------------------------------------------------------------------------------------------------------------------------------- | :------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| **ARC-01**       | [System Architecture Overview](documentation/03_System_Architecture/ARC-01_System_Architecture_Overview.md)                          | **Approved**               | 7-layer architecture, 7 external actors, system boundaries, and 10 non-negotiables.                                |
| **ARC-02**       | [Principles, Standards & Constraints](documentation/03_System_Architecture/ARC-02_Architectural_Principles_Standards_Constraints.md) | **Approved & Implemented** | Principles P-01 to P-10, Constraints CON-01 to CON-16, 10 Work Packages, and 32 tests.                             |
| **ARC-03**       | [Application Architecture](documentation/03_System_Architecture/ARC-03_Application_Architecture.md)                                  | **Approved & Implemented** | Modular monolith, Next.js 14 + FastAPI, Layered boundaries, Repository & UoW, 46 tests.                            |
| **ARC-04**       | [Modular Domain Architecture](documentation/03_System_Architecture/ARC-04_Modular_Domain_Architecture.md)                            | **Approved & Implemented** | 16 discrete domain modules, 18 domain events, pure domain entities, AST checks, 94 tests.                          |
| **ARC-05**       | [Multi-Tenant Architecture](documentation/03_System_Architecture/ARC-05_Multi_Tenant_Architecture.md)                                | **Approved & Implemented** | Organization primary tenancy, 8-layer defense in depth, PostgreSQL RLS, storage/cache isolation, 144 tests.        |
| **ARC-06**       | [Data Architecture](documentation/03_System_Architecture/ARC-06_Data_Architecture.md)                                                | **Approved & Implemented** | Relational schema, composite FKs, 30+ SQLAlchemy models, immutable published snapshots, 199 tests.                 |
| **ARC-07**       | [API & Integration Architecture](documentation/03_System_Architecture/ARC-07_API_Integration_Architecture.md)                        | **Approved & Implemented** | REST API (/api/v1), 66 endpoints, OpenAPI 3.1, TypeScript SDK, server-derived tenancy, outbox webhooks, 274 tests. |
| **ARC-08**       | [Theme & Customization Architecture](documentation/03_System_Architecture/ARC-08_Theme_Customization_Architecture.md)                | **Approved & Implemented** | Configuration-driven, token taxonomy, 6 themes, 4 layouts, 13 components, dual-editor parity, 378 tests.           |
| **ARC-09**       | Menu Rendering Architecture                                                                                                          | _Roadmap_                  | Mobile webview optimization, category jump scrolling, and SSR caching.                                             |
| **ARC-10**       | Publishing & Versioning Lifecycle                                                                                                    | _Roadmap_                  | Snapshot compiling, SHA-256 digest validation, and zero-downtime rollback.                                         |
| **ARC-11**       | Infrastructure & Deployment                                                                                                          | _Roadmap_                  | Docker compose, multi-profile environment handling, and backup/restore.                                            |
| **ARC-12**       | Security, Scalability & Reliability                                                                                                  | _Roadmap_                  | Threat modeling, penetration verification, rate limiting, and failover.                                            |

---

## 📁 Repository Structure

```text
Menu-it/
├── .github/
│   ├── workflows/quality-gates.yml          # GitHub Actions CI with 7 automated quality gates
│   ├── CODEOWNERS                           # Module ownership and approval requirements
│   ├── CONTRIBUTING.md                      # Engineering standards, commit conventions & PR rules
│   └── pull_request_template.md             # Architecture compliance checklist for pull requests
├── backend/
│   ├── app/
│   │   ├── api/                             # API delivery layer
│   │   │   ├── dependencies.py              # Auth, tenant verification, and role guards
│   │   │   ├── router.py                    # Consolidated API v1 router
│   │   │   └── v1/                          # Versioned route controllers
│   │   │       ├── auth.py                  # User registration, login, JWT issuance
│   │   │       ├── menus.py                 # Menu, category, and food item management
│   │   │       ├── platform.py              # Platform admin overview and metrics
│   │   │       ├── public.py                # Anonymous diner QR read and PNG generator
│   │   │       ├── publishing.py            # Atomic snapshot publishing and version pointers
│   │   │       ├── restaurants.py           # Restaurant profile & membership management
│   │   │       └── themes.py                # Preset listing & restaurant design token updates
│   │   ├── core/                            # Cross-cutting application infrastructure
│   │   │   ├── config.py                    # Dual-profile environment configuration
│   │   │   ├── database.py                  # SQLAlchemy 2.0 Async session & GUID adapters
│   │   │   ├── errors.py                    # RFC 7807 Problem Details exception handlers
│   │   │   ├── security.py                  # Bcrypt hashing & JWT cryptographic tokens
│   │   │   └── tenant_context.py            # ContextVar-based tenant execution tracking
│   │   ├── modules/                         # Domain models and schemas
│   │   │   ├── identity/                    # Users, Organizations, Restaurants, Members
│   │   │   ├── menus/                       # Menus, Categories, Items, Variants, Snapshots
│   │   │   └── themes/                      # Themes, Design Configs, and 6 visual presets
│   │   ├── main.py                          # FastAPI application initialization & middleware
│   │   └── seed.py                          # Deterministic database seeding pipeline
│   ├── migrations/                          # Alembic schema migrations
│   ├── Dockerfile                           # Production container definition
│   ├── pyproject.toml                       # Ruff linter & Pytest configuration
│   └── requirements.txt                     # Pinned backend dependencies
├── frontend/
│   ├── src/
│   │   ├── app/                             # Next.js 14 App Router
│   │   │   ├── page.tsx                     # Landing page & Portal Launcher
│   │   │   ├── layout.tsx                   # Root HTML shell with design token fonts
│   │   │   ├── app/page.tsx                 # 3-Panel Visual Studio & Catalog Builder
│   │   │   ├── platform/page.tsx            # Multi-Tenant Platform Administration Dashboard
│   │   │   └── r/[slug]/page.tsx            # Public Diner Mobile Webview & Table QR Modal
│   │   └── lib/
│   │       ├── api.ts                       # Typed REST API client
│   │       ├── themes.ts                    # Design token definitions & CSS variable compiler
│   │       └── utils.ts                     # UI utility functions
│   ├── package.json                         # Frontend dependencies (React 18, Tailwind, Lucide)
│   ├── tailwind.config.ts                   # Tailwind theme variable mappings
│   └── tsconfig.json                        # TypeScript strict compiler options
├── docs/
│   ├── decisions/
│   │   ├── ADR-TEMPLATE.md                  # Standardized architectural decision template
│   │   └── decision-register.md             # Decision register (ADR-0001 through ADR-0012)
│   ├── governance/
│   │   ├── architecture-review-policy.md    # Formal governance policy & authority hierarchy
│   │   └── architecture-compliance-checklist.md # Actionable PR compliance checklist
│   └── reports/
│       ├── ARC-02-compliance-report.md      # 15/15 item compliance audit report
│       ├── ARC-02-test-report.md            # Complete 32-test execution breakdown
│       ├── ARC-02-security-review.md        # OWASP A01 & tenant isolation security audit
│       ├── ARC-02-deviation-register.md     # Active architectural deviations (Zero deviations)
│       └── ARC-02-approval-record.md        # Review board sign-off record
├── packages/
│   ├── README.md                            # Shared contracts package guide
│   └── contracts/
│       ├── theme_schema.json                # JSON Schema for Design Tokens & Presets
│       ├── component_registry.json          # Allowlisted UI component registry
│       └── published_snapshot.json          # Schema for compiled menu snapshots
├── scripts/
│   └── validate_arc02_e2e.py                # 10-step formal end-to-end V&V script
├── tests/
│   ├── conftest.py                          # Shared async SQLite fixture with model preloading
│   ├── architecture/
│   │   └── test_module_boundaries.py        # AST parser: no private imports, no circular imports
│   ├── contract/
│   │   └── test_openapi_contracts.py        # OpenAPI 3.1 & REST verb contract checks
│   ├── integration/
│   │   ├── test_operational_health.py       # Health probes (/health) & Redis resilience
│   │   └── test_publishing_immutability.py   # Snapshot immutability & catalog decoupling
│   ├── security/
│   │   ├── test_auth.py                     # Bcrypt + JWT authentication tests
│   │   └── test_tenant_security.py         # Cross-tenant 403 checks & platform admin guards
│   └── unit/
│       ├── test_monetary_and_schema.py      # Decimal pricing (CON-05) & slug kebab-case regex
│       ├── test_rfc7807_errors.py           # Problem details formatting & pagination 422
│       └── test_theme_tokens.py             # Hex color regex & component visibility toggling
├── docker-compose.yml                       # Multi-container orchestration (App + Postgres + Caddy)
├── LICENSE                                  # Commercial Software License Agreement
└── README.md                                # Master project documentation
```

---

## 🚀 Quickstart & Local Setup

### Prerequisites

- **Python:** 3.12+
- **Node.js:** 20+ (with `pnpm` installed: `npm i -g pnpm`)
- **Docker & Docker Compose:** Optional for containerized deployment

### 1. Backend Service Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the database seeding pipeline (creates admin, demo restaurants, categories, dishes & v1 snapshots)
python -m app.seed

# Run the test suite (32 tests across architecture, security, integration, unit)
pytest -v

# Launch the FastAPI application server
uvicorn app.main:app --reload --port 8000
```

- **API Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Contract View:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Service Health Probe:** [http://localhost:8000/health](http://localhost:8000/health)

### 2. Frontend Web Application Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies using pnpm
pnpm install

# Verify production build & bundle size budget (<120 kB)
pnpm run build

# Start local Next.js development server
pnpm run dev
```

- **Portal Launcher & Showcase:** [http://localhost:3000](http://localhost:3000)
- **3-Panel Visual Studio:** [http://localhost:3000/app](http://localhost:3000/app)
- **Platform Administration:** [http://localhost:3000/platform](http://localhost:3000/platform)
- **Public Diner QR Menu (Demo):** [http://localhost:3000/r/the-bombay-canteen](http://localhost:3000/r/the-bombay-canteen)

### 3. Full-Stack Docker Compose Deployment

```bash
# Build and start all services (PostgreSQL 16, FastAPI backend, Next.js frontend)
docker compose up -d --build

# View container logs
docker compose logs -f
```

---

## 🧪 Automated Quality Gates & Verification

The repository enforces strict automated quality gates prior to any pull request merge:

### 1. Pytest Test Suites (618 Tests Passing — 100% Pass Rate)

```bash
pytest tests/ -v
# ======================== 618 passed in 60.63s ========================
```

- **Architecture Boundaries (`tests/architecture/`):** Uses Python AST parsing to guarantee domain models never import the API layer or HTTP frameworks, verifies zero circular dependencies between all 16 modules, and mandates `lazy="raise"` on all SQLAlchemy relationships.
- **Security & Tenancy (`tests/security/`):** 50 multi-tenant test scenarios (`ARC05-T001` to `ARC05-T050`) verifying that Tenant A is rejected with `HTTP 403 Forbidden` when attempting to access Tenant B's catalog or design settings, verifying transaction-local PostgreSQL RLS context, and preventing IDOR attacks.
- **Database & Persistence Integrity (`tests/database/`):** 55 test scenarios (`ARC06-T001` to `ARC06-T055`) proving composite foreign key enforcement, default price uniqueness via partial indexes, JSONB configuration validation, and optimistic concurrency locking.
- **Contract & Standards (`tests/contract/`, `tests/unit/`):** Enforces RFC 7807 problem details error envelopes, OpenAPI 3.1 specification validity, and exact Python `Decimal` currency representation.
- **Snapshot Immutability (`tests/integration/`):** Proves that published snapshots are write-once, read-many (WORM) with SHA-256 digests and ORM mutation guards rejecting `UPDATE` and `DELETE`.
- **Customization Engine (`tests/customization/`):** 104 test scenarios (`ARC08-T001` to `ARC08-T104`) verifying theme token resolution, responsive layouts, component slots, and dual-editor parity.
- **Menu Rendering Engine (`tests/rendering/`):** 120 test scenarios (`ARC09-T001` to `ARC09-T120`) verifying pure presentation engine composition, ETag HTTP 304 caching, and First Load JS budget (< 120 kB).
- **Publishing & Versioning Engine (`tests/publishing/`):** 120 test scenarios (`ARC10-T001` to `ARC10-T120`) verifying draft revisioning, validation readiness, atomic activation, non-destructive rollback, and transactional outbox events.

### 2. Formal End-to-End Product Validation Script

Execute the formal multi-step validation scenario:

```bash
python scripts/validate_arc02_e2e.py
```

_Output validates:_ Restaurant provisioning ➔ Catalog creation ➔ Theme preset selection ➔ Design token overrides ➔ Layout custom configuration ➔ Component registry toggles ➔ Studio draft preview ➔ Atomic snapshot publication with SHA-256 digest ➔ Anonymous zero-auth diner read ➔ Dynamic QR PNG generation.

---

## 📚 Engineering Chronicles: Devlogs & Tasklogs

Detailed milestone execution and developer journals are documented in dedicated archives:

- **[Developer Logs (Devlogs)](docs/devlogs/README.md):** 13 comprehensive engineering chronicles:
  - [Devlog-001: Project Initialization & Blueprint Baseline](docs/devlogs/devlog-001-project-initialization-and-blueprint.md)
  - [Devlog-002: ARC-01 System Architecture Overview](docs/devlogs/devlog-002-arc01-system-architecture-overview.md)
  - [Devlog-003: ARC-02 Principles, Standards & Constraints](docs/devlogs/devlog-003-arc02-architectural-principles-and-standards.md)
  - [Devlog-004: ARC-03 Application Architecture](docs/devlogs/devlog-004-arc03-application-architecture.md)
  - [Devlog-005: ARC-04 Modular Domain Architecture](docs/devlogs/devlog-005-arc04-modular-domain-architecture.md)
  - [Devlog-006: ARC-05 Multi-Tenant Architecture](docs/devlogs/devlog-006-arc05-multi-tenant-architecture.md)
  - [Devlog-007: ARC-06 Data Architecture & Persistence](docs/devlogs/devlog-007-arc06-data-architecture-and-persistence.md)
  - [Devlog-008: ARC-07 API & Integration Architecture](docs/devlogs/devlog-008-arc07-api-and-integration-architecture.md)
  - [Devlog-009: ARC-08 Theme & Customization Architecture](docs/devlogs/devlog-009-arc08-theme-and-customization-architecture.md)
  - [Devlog-010: ARC-09 Menu Rendering Architecture](docs/devlogs/devlog-010-arc09-menu-rendering-architecture.md)
  - [Devlog-011: ARC-10 Publishing & Versioning Architecture](docs/devlogs/devlog-011-arc10-publishing-versioning-architecture.md)
  - [Devlog-012: CI/CD Quality Gates & Jobs Remediation](docs/devlogs/devlog-012-ci-cd-quality-gates-and-jobs-remediation.md)
  - [Devlog-013: ARC-11 Infrastructure & Deployment Architecture](docs/devlogs/devlog-013-arc11-infrastructure-deployment.md)
  - [Devlog-014: ARC-12 Security, Scalability & Reliability Architecture](docs/devlogs/devlog-014-arc12-security-scalability-reliability.md)
- **[Task Execution Logs (Tasklogs)](docs/tasklogs/README.md):** Task verification logs and work package breakdowns:
  - [Tasklog-ARC01: System Overview Tasks](docs/tasklogs/tasklog-arc01-overview.md)
  - [Tasklog-ARC02: Engineering Standards (WP-01 to WP-10)](docs/tasklogs/tasklog-arc02-principles.md)
  - [Tasklog-ARC03: Application Architecture (WP-01 to WP-10)](docs/tasklogs/tasklog-arc03-application.md)
  - [Tasklog-ARC04: Modular Domain Architecture (WP-01 to WP-10)](docs/tasklogs/tasklog-arc04-domain.md)
  - [Tasklog-ARC05: Multi-Tenant Architecture (WP-01 to WP-12)](docs/tasklogs/tasklog-arc05-multitenant.md)
  - [Tasklog-ARC06: Data Architecture & Persistence (WP-01 to WP-12)](docs/tasklogs/tasklog-arc06-data.md)
  - [Tasklog-ARC07: API & Integration Architecture (WP-01 to WP-12)](docs/tasklogs/tasklog-arc07-api.md)
  - [Tasklog-ARC08: Theme & Customization Architecture (WP-01 to WP-13)](docs/tasklogs/tasklog-arc08-customization.md)
  - [Tasklog-ARC09: Menu Rendering Architecture (WP-01 to WP-15)](docs/tasklogs/tasklog-arc09-rendering.md)
  - [Tasklog-ARC10: Publishing & Versioning Architecture (WP-01 to WP-15)](docs/tasklogs/tasklog-arc10-publishing.md)
  - [Tasklog-ARC11: Infrastructure & Deployment Architecture (WP-01 to WP-14)](docs/tasklogs/tasklog-arc11-infrastructure.md)
  - [Tasklog-ARC12: Security, Scalability & Reliability (WP-01 to WP-15)](docs/tasklogs/tasklog-arc12-security.md)

---

## 📜 Architectural Decision Records (ADRs)

All core engineering choices are tracked in [`docs/decisions/decision-register.md`](docs/decisions/decision-register.md) (256 decisions recorded):

- **ADR-0001 to ADR-0012:** System Architecture Principles & Non-Negotiable Standards (ARC-01 / ARC-02)
- **ADR-0013 to ADR-0027:** Application Architecture, Layering & Monolith Boundaries (ARC-03)
- **ADR-0028 to ADR-0043:** Modular Domain Architecture, 16 Discrete Modules & Domain Events (ARC-04)
- **ADR-0044 to ADR-0063:** Multi-Tenant Architecture, 8-Layer Defense in Depth & Fail-Closed RLS (ARC-05)
- **ADR-0064 to ADR-0088:** Data Architecture, Composite Foreign Keys & Immutable Snapshot Persistence (ARC-06)
- **ADR-0089 to ADR-0113:** API & Integration Architecture, Contract-First OpenAPI & Webhooks (ARC-07)
- **ADR-0114 to ADR-0140:** Theme & Customization Architecture, Design Tokens & Component Slots (ARC-08)
- **ADR-0141 to ADR-0167:** Menu Rendering Architecture, Pure Engine, Snapshots & High-Concurrency Caching (ARC-09)
- **ADR-0168 to ADR-0191:** Publishing & Versioning Architecture, Atomic Activation, Rollback & Outbox (ARC-10)
- **ADR-0192 to ADR-0221:** Infrastructure & Deployment Architecture, Dual Profiles, Non-Root Containers, HMAC Local Storage & DR (ARC-11)
- **ADR-0222 to ADR-0256:** Security, Scalability & Reliability Architecture, Argon2id, RBAC, RLS Defense, Circuit Breakers & DLQ (ARC-12)

---

## 📄 License & Commercial Rights

Copyright © 2026 Sahil Khutey. All Rights Reserved.

This software is released under a **Commercial Software License Agreement**. Unauthorized copying, modification, distribution, public hosting as a competing SaaS offering, or sublicensing of this software, via any medium, is strictly prohibited.

For commercial licensing, enterprise self-hosted appliances, or white-label partnerships, please refer to [LICENSE](LICENSE) or contact:

- **Author & Copyright Holder:** Sahil Khutey
- **Repository:** [https://github.com/SahilKhutey/Menu-It.git](https://github.com/SahilKhutey/Menu-It.git)

---

## 🏷️ Tags & Keywords

`restaurant-menu` · `digital-menu` · `qr-code-menu` · `multi-tenant` · `fastapi` · `nextjs14` · `react18` · `tailwindcss` · `postgresql-rls` · `sqlalchemy-async` · `pydantic-v2` · `fssai-dietary-badges` · `saas-architecture` · `zero-fork` · `design-tokens`
