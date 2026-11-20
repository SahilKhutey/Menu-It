# 13 — Domain Architecture Testing Strategy & Catalogue

**Specification:** ARC-04 §14  
**Project:** ModularMenu  

---

## 1. Domain Testing Levels

ModularMenu verifies domain logic across seven distinct testing tiers:
1. **Domain Unit Tests:** Pure business rules and invariants (`Money`, `EmailAddress`, `Menu`). Zero I/O.
2. **Application Unit Tests:** Use case orchestration with in-memory test doubles (`CreateMenuUseCase`).
3. **Contract Tests:** Conformance to public Python Protocols (`CategoryReader`, `PublishedSnapshotReader`).
4. **Integration Tests:** Cooperating module workflows and database transactional integrity.
5. **Architecture Boundary Tests:** AST-based static analysis enforcing directional imports and zero circular coupling.
6. **Workflow Tests:** End-to-end multi-module journeys (Onboarding, Publishing, Rollback).
7. **Regression Tests:** Immutable snapshot protection and currency fixed-precision arithmetic.

---

## 2. 50-Test Catalogue Verification Matrix

| Test ID Range | Target Domain / Subsystem | Execution Suite | Status |
| :--- | :--- | :--- | :--- |
| **ARC04-T001 to T004** | MOD-01 Identity & Auth | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T005 to T007** | MOD-02 Organization & Tenant | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T008 to T009** | MOD-03 Restaurant Management | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T010 to T011** | MOD-04 Menu Management | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T012 to T014** | MOD-05 Category Management | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T015 to T017** | MOD-06 Food Item Management | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T018 to T020** | MOD-07 Pricing & Availability | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T021 to T022** | MOD-08 Theme Engine | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T023 to T024** | MOD-09 Layout Engine | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T025 to T027** | MOD-10 Component Registry | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T028 to T030** | MOD-11 Menu Rendering Engine | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T031 to T033** | MOD-12 Visual Menu Editor | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T034 to T037** | MOD-13 Publishing & Versioning | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T038 to T040** | MOD-14 Media Management | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T041 to T043** | MOD-15 Subscription & Licensing | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T044 to T045** | MOD-16 Analytics & Integrations | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |
| **ARC04-T046 to T047** | Cross-Module Architecture Boundaries | `tests/architecture/test_arc04_boundaries.py` | **PASSED** |
| **ARC04-T048 to T050** | Cross-Module Workflows & Parity | `tests/unit/test_arc04_domain_catalogue.py` | **PASSED** |

**Execution Summary:** 94 / 94 tests passing across the entire repository (100% pass rate in 11.47s).
