# ModularMenu Architecture Index

Welcome to the **ModularMenu** (Menu-It) architecture documentation index.

This platform follows a strict architectural governance hierarchy governed by formal specifications:

```
Level 1 — System Architecture
├── ARC-01: System Architecture Overview
│   └── High-level system definition, 7 external actors, system boundaries, and 10 invariants.
├── ARC-02: Architectural Principles, Standards & Constraints
│   └── 10 governing principles (P-01 to P-10), 16 constraints (CON-01 to CON-16), and 7 quality gates.
└── ARC-03: Application Architecture (Modular Monolith)
    └── Frontend/backend separation, application/domain layers, service/repository patterns, and request lifecycles.
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

---

## 🛠️ Architectural Governance & Decisions

- **[ADR Register](docs/decisions/decision-register.md):** Permanent records of all major technical decisions (ADR-0001 through ADR-0027).
- **[Architecture Review Policy](docs/governance/architecture-review-policy.md):** Formal decision hierarchy and review authority.
- **[Compliance Checklist](docs/governance/architecture-compliance-checklist.md):** PR quality gates for principles and constraints.
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
