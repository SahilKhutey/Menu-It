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
└── ARC-05: Multi-Tenant Architecture & Isolation Model
    └── Organization-based tenancy, 8-layer defense in depth, PostgreSQL RLS fail-closed policies, and 50-test security suite.
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

---

## 🛠️ Architectural Governance & Decisions

- **[ADR Register](docs/decisions/decision-register.md):** Permanent records of all major technical decisions (ADR-0001 through ADR-0063).
- **[Architecture Review Policy](docs/governance/architecture-review-policy.md):** Formal decision hierarchy and review authority.
- **[Compliance Checklist](docs/governance/architecture-compliance-checklist.md):** PR quality gates for principles and constraints.
- **[Domain Architecture Suite](docs/architecture/ARC-04-modular-domain-architecture/):** Detailed specifications for MOD-01 to MOD-16, workflows, and risk register.
- **[Multi-Tenant Architecture Suite](docs/architecture/ARC-05-multi-tenant-architecture/):** Complete specifications for multi-tenancy, RLS policies, threat models, and risk register.
- **[Shared Contracts](packages/contracts/):** JSON schemas for Theme Tokens, Component Registry, and Published Snapshots.

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
