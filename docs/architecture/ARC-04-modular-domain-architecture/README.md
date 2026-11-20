# ARC-04 — Modular Domain Architecture

**Specification ID:** ARC-04  
**Project:** ModularMenu / Menu-It  
**Architecture Level:** Domain Decomposition & Bounded Contexts  
**Status:** Approved Architectural Baseline  
**Governing Standard:** Modular Monolith with In-Process Contracts  

---

## 1. Scope & Directory Navigation

This documentation suite establishes the formal business domain model, bounded contexts, module boundaries, entity lifecycle, and inter-module contracts for ModularMenu.

```
docs/architecture/ARC-04-modular-domain-architecture/
├── README.md                                  # Index and architecture summary
├── 01-domain-architecture-overview.md         # Domain capability map and 5 functional groups
├── 02-bounded-contexts.md                     # Bounded context decomposition
├── 03-module-ownership-matrix.md              # Authoritative ownership rules
├── 04-module-specifications/                  # 16 detailed module specifications (MOD-01 to MOD-16)
│   ├── MOD-01-identity.md
│   ├── MOD-02-organizations.md
│   ├── MOD-03-restaurants.md
│   ├── MOD-04-menus.md
│   ├── MOD-05-categories.md
│   ├── MOD-06-food-items.md
│   ├── MOD-07-pricing-availability.md
│   ├── MOD-08-themes.md
│   ├── MOD-09-layouts.md
│   ├── MOD-10-components.md
│   ├── MOD-11-rendering.md
│   ├── MOD-12-editor.md
│   ├── MOD-13-publishing.md
│   ├── MOD-14-media.md
│   ├── MOD-15-licensing.md
│   └── MOD-16-analytics-integrations.md
├── 05-domain-models.md                        # Domain entities and value objects
├── 06-aggregate-boundaries.md                 # Transactional consistency boundaries
├── 07-module-contracts.md                     # Python Protocol contracts and interfaces
├── 08-dependency-architecture.md              # Directional dependency graph & rules
├── 09-domain-events.md                        # Catalogue of 18 domain events (EVT-001 to EVT-018)
├── 10-business-workflows.md                   # Core business workflows (Onboarding, Menu, Publishing)
├── 11-transaction-consistency.md              # Synchronous DB transactions vs eventual consistency
├── 12-extensibility-architecture.md           # Progressive extensibility & safe component registry
├── 13-testing-strategy.md                     # Domain test levels and 50-test catalogue
├── 14-verification-validation.md              # Verification matrix and validation scenarios
├── 15-implementation-work-packages.md         # 10 work packages (WP-ARC04-01 to WP-ARC04-10)
├── 16-risk-register.md                        # Risk evaluation and mitigation strategy
├── 17-architecture-decisions.md               # 16 architectural decisions (ARC04-D01 to ARC04-D16)
└── 18-compliance-report.md                    # Formal architecture sign-off and audit report
```
