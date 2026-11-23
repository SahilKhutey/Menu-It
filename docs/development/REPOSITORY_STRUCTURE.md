# Menu-It — Monorepo Architecture & Repository Structure

**Document ID:** FCD01-DOC-03  
**Phase:** FCD-01 Development Environment & Repository Foundation  
**Audience:** All Software Engineers & System Architects  

---

## 1. Architectural Philosophy

Menu-It is organized as a **Modular Monorepo**. This structure maintains strict module isolation while enabling:
1. **Single Source of Truth:** Uniform versioning, shared contracts, unified CI quality gates.
2. **Strict Boundary Enforcement:** Clear ownership boundaries between frontend presentation, backend business domain logic, database migrations, and shared packages.
3. **Decoupled Deployment Parity:** Shared code executes identically whether deployed to the **Managed SaaS** multi-tenant cloud or the **Customer-Hosted** single-tenant appliance.

---

## 2. Directory Hierarchy

```
menu-it/
├── backend/                     # FastAPI modular monolith entrypoint & core
│   ├── app/                     # Domain modules, core services, middleware, security
│   ├── migrations/              # Alembic database migrations (expand & contract)
│   ├── openapi/                 # OpenAPI 3.1 schema specifications
│   ├── requirements.txt         # Pinned backend production dependencies
│   ├── pyproject.toml           # Ruff and build configuration
│   └── alembic.ini              # Database migration configuration
│
├── frontend/                    # Customer-facing Next.js 14 web application
│   ├── src/                     # App router, components, hooks, lib, providers
│   ├── public/                  # Static assets and public images
│   ├── package.json             # Frontend dependency manifest
│   ├── tailwind.config.ts       # Tailwind CSS configuration
│   └── tsconfig.json            # Strict TypeScript compiler options
│
├── packages/                    # Reusable, framework-agnostic shared libraries
│   ├── contracts/               # Shared TypeScript schemas, API contracts, DTOs
│   ├── design-tokens/           # Centralized theme tokens, colors, typography scales
│   ├── theme-engine/            # Theme compilation, validation, CSS variable generation
│   ├── menu-renderer/           # Decoupled public diner menu presentation engine
│   ├── editor-engine/           # Menu builder and layout customization engine
│   └── component-registry/      # Component catalog, schema definitions, defaults
│
├── database/                    # Database lifecycle assets
│   ├── migrations/              # Migration scripts and history
│   ├── schemas/                 # Canonical relational DDL schemas
│   └── seeds/                   # Tenant and demonstration seed data
│
├── infrastructure/              # Infrastructure and deployment automation
│   ├── compose/                 # Docker Compose profiles (dev, staging, production)
│   ├── docker/                  # Multi-stage Dockerfiles (frontend, backend, worker)
│   ├── proxy/                   # Nginx reverse proxy, TLS, and security configs
│   ├── manifests/               # Declarative deployment and capacity profiles
│   ├── security/                # Security policies, threat registers, schemas
│   ├── reliability/             # SLO catalogues, retry policies, recovery objectives
│   └── scripts/                 # Preflight, build, deploy, migrate, backup scripts
│
├── tests/                       # Platform-wide automated verification suites
│   ├── unit/                    # Pure isolated unit tests
│   ├── integration/             # Multi-component and database integration tests
│   ├── architecture/            # Boundary enforcement and import rule tests (AST)
│   ├── contract/                # OpenAPI and frontend contract parity tests
│   ├── security/                # OWASP, RLS, tenant isolation, and cryptographic tests
│   ├── e2e/                     # End-to-end user workflow simulations
│   └── fixtures/                # Reusable test payloads and mocks
│
├── docs/                        # Complete technical and operational documentation
│   ├── architecture/            # Architecture specifications (ARC-01 to ARC-12)
│   ├── development/             # Developer guides, environment, setup, and reports
│   ├── engineering/             # Coding standards, git workflow, dependency policies
│   ├── security/                # Security standards, checklists, threat models
│   ├── reliability/             # SLOs, capacity planning, failover runbooks
│   ├── devlogs/                 # Chronological developer log chronicles
│   └── tasklogs/                # Detailed milestone work package execution logs
│
├── scripts/                     # Developer tooling and automation
│   ├── setup/                   # Workspace initialization scripts
│   ├── development/             # Development lifecycle orchestration scripts
│   ├── validation/              # Automated environment and preflight checks
│   └── maintenance/             # Database maintenance and housekeeping tools
│
├── .github/                     # GitHub Actions CI/CD workflows and templates
│   ├── workflows/               # Automated CI quality gates and API verification
│   └── PULL_REQUEST_TEMPLATE.md # Standard PR submission checklist
│
├── .editorconfig                # Universal indentation and encoding standards
├── .prettierrc.json             # Code formatting configuration
├── .gitignore                   # Git exclusion rules
├── .env.example                 # Baseline environment configuration template
├── README.md                    # Project overview and entry point
├── CONTRIBUTING.md              # Engineering contribution guide
└── SECURITY.md                  # Vulnerability reporting and security requirements
```

---

## 3. Workspace Responsibilities & Anti-Patterns

| Workspace / Directory | Allowed Responsibilities | Forbidden Patterns (Must NOT Contain) |
| :--- | :--- | :--- |
| `frontend/` | Customer presentation, responsive UI, routing, state management | Direct database access, business rules bypassing backend, plaintext secrets |
| `backend/` | Domain logic, data access, authentication, validation, orchestration | Frontend components, HTML generation (except minimal emails), static UI bundles |
| `packages/*` | Pure reusable algorithms, contracts, tokens, renderers | Direct database drivers, runtime secrets, circular imports between packages |
| `database/` | Schemas, migration history, seed definitions | Application-specific business routing or frontend styling |
| `infrastructure/` | Container definitions, orchestration manifests, network scripts | Domain entity business logic or product features |
| `tests/` | Automated test suites, fixtures, assertions, test runners | Production application source code or unmocked live secrets |
| `docs/` | Architectural specifications, runbooks, devlogs, guides | Unverified assumptions or temporary scratch notes |

---

## 4. Cross-Language Contract Boundaries

```
[ frontend/ ] ──(REST / JSON API)──> [ backend/app/api/ ]
     │                                      │
     ▼                                      ▼
[ packages/contracts ]               [ backend/openapi/ ]
(TypeScript types)                   (OpenAPI 3.1 Spec)
```

1. **Schema Generation:** The OpenAPI 3.1 specification emitted by the backend is the authoritative contract.
2. **TypeScript Types:** Types in `packages/contracts/` must maintain 100% parity with OpenAPI definitions.
3. **No Direct Code Sharing:** Python backend never imports TypeScript files; communication is strictly over versioned JSON payloads validated at runtime by Pydantic.
