# 16 — Domain Architecture Risk Register

**Specification:** ARC-04 §18  
**Project:** ModularMenu  

---

## 1. Domain Risk Evaluation & Mitigation Matrix

| Risk ID | Risk Description | Severity | Mitigation Strategy | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ARC04-R01** | Modules overlap in responsibility | High | Strict 16-module ownership matrix; single authoritative owner per concept. | **MITIGATED** |
| **ARC04-R02** | Excessive cross-module coupling | High | Communication restricted strictly to Python Protocols and domain events. | **MITIGATED** |
| **ARC04-R03** | Circular module dependencies | High | Directional dependency map enforced via automated AST CI tests. | **MITIGATED** |
| **ARC04-R04** | Shared package becomes a dumping ground | Medium | Strict admission criteria: only pure generic primitives (`Money`, `EmailAddress`). | **MITIGATED** |
| **ARC04-R05** | Overly large aggregates | High | Fine-grained aggregate roots referencing peers by UUID, not object pointers. | **MITIGATED** |
| **ARC04-R06** | Premature distributed event buses | Medium | In-process domain event dispatch; no message brokers required. | **MITIGATED** |
| **ARC04-R07** | Direct ORM access across modules | High | AST boundary test `test_arc04_t047_no_direct_cross_module_orm_access`. | **MITIGATED** |
| **ARC04-R08** | Editor & renderer config diverges | Critical | Shared versioned schemas in `packages/contracts` and `MOD-10`. | **MITIGATED** |
| **ARC04-R09** | Publication reads inconsistent state | Critical | Transactional candidate snapshot assembly and immutable SHA-256 storage. | **MITIGATED** |
| **ARC04-R10** | Theme/layout/component mismatch | High | Slot compatibility validation in `LayoutDefinition.validate_slot_compatibility`. | **MITIGATED** |
| **ARC04-R11** | Optional modules become hard dependencies| Medium | Graceful fallback in core menu paths when media or analytics are absent. | **MITIGATED** |
| **ARC04-R12** | SaaS-specific logic leaks into domain | High | Clean separation: domain logic is 100% deployment-profile neutral. | **MITIGATED** |
| **ARC04-R13** | Module changes break integrations | High | Automated contract tests and schema versioning. | **MITIGATED** |
| **ARC04-R14** | Inadequate domain auditability | Medium | Standardized domain events (EVT-001 to EVT-018) emitted for state changes. | **MITIGATED** |
| **ARC04-R15** | Custom components introduce security risks| Critical | Pre-approved component registry; arbitrary script/HTML uploads banned. | **MITIGATED** |

---

## 2. Critical Release-Gating Risks Resolution
- **R-09 (Publication Consistency):** `PublishedVersion` aggregates freeze candidate snapshots with SHA-256 digests. Active version pointers update atomically in a single transaction.
- **R-08 (Configuration Compatibility):** `MOD-10` property schema validation guarantees the renderer receives only valid, renderable tokens.
- **R-15 (Component Execution Security):** All UI components are mapped to allowlisted built-in React components. No executable code is uploaded or executed dynamically.
