# 14 — Verification & Validation Framework

**Specification:** ARC-04 §15  
**Project:** ModularMenu  

---

## 1. Verification Matrix (ARC04-VER-01 to ARC04-VER-12)

| Verification Activity | Target Subsystem | Evidence | Result |
| :--- | :--- | :--- | :--- |
| **ARC04-VER-01** | Module Ownership | `docs/architecture/ARC-04-modular-domain-architecture/03-module-ownership-matrix.md` | **VERIFIED** |
| **ARC04-VER-02** | Module Boundaries | 16 module specifications in `04-module-specifications/` | **VERIFIED** |
| **ARC04-VER-03** | Import Graph Inspection | `backend/architecture/module_dependencies.yaml` | **VERIFIED** |
| **ARC04-VER-04** | Contract Ownership | Typed Python Protocols in each module's `contracts.py` | **VERIFIED** |
| **ARC04-VER-05** | Aggregate Boundaries | `06-aggregate-boundaries.md` | **VERIFIED** |
| **ARC04-VER-06** | Domain Unit Tests | `tests/unit/test_arc04_domain_catalogue.py` (45 tests) | **VERIFIED** |
| **ARC04-VER-07** | Contract Tests | Protocol conformance across all 16 modules | **VERIFIED** |
| **ARC04-VER-08** | Integration Tests | Multi-module test cases passing | **VERIFIED** |
| **ARC04-VER-09** | Event Contracts | `app.shared.domain.events` (EVT-001 to EVT-018) | **VERIFIED** |
| **ARC04-VER-10** | Transaction Consistency | Synchronous UoW vs eventual consistency strategy | **VERIFIED** |
| **ARC04-VER-11** | Edition Neutrality | Verified by `test_arc04_t050_edition_neutrality_domain_execution` | **VERIFIED** |
| **ARC04-VER-12** | Extension Safety | Component registry property validation in `MOD-10` | **VERIFIED** |

---

## 2. Validation Scenarios (VAL-ARC04-01 to VAL-ARC04-06)

- **VAL-ARC04-01 (Restaurant Onboarding):** User registers -> creates Org -> creates Restaurant. Verified by `test_arc04_t049_restaurant_onboarding_workflow`.
- **VAL-ARC04-02 (Menu Content Management):** Structured creation of menus, categories, food items, and money prices.
- **VAL-ARC04-03 (Design Customization):** Schema-validated theme tokens and layout compatibility.
- **VAL-ARC04-04 (Publication Integrity):** Immutable snapshots with SHA-256 digests; later edits leave active snapshots unchanged.
- **VAL-ARC04-05 (Deployment Parity):** Identical domain rules execute cleanly in SaaS and customer-hosted profiles.
- **VAL-ARC04-06 (Module Extensibility):** New component schemas integrate without altering core domain entities.
