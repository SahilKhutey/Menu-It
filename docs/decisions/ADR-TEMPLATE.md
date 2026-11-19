# ADR-XXXX: [Short Title of Architectural Decision]

**Document ID:** ADR-XXXX  
**Status:** [Proposed | Accepted | Rejected | Deprecated | Superseded]  
**Deciders:** [System Architect, Backend Lead, Frontend Lead, DevOps Lead]  
**Date:** [YYYY-MM-DD]  
**Governing Architecture:** ARC-01 (System Architecture Overview), ARC-02 (Principles, Standards & Constraints)

---

## 1. Context & Problem Statement

Describe the specific context, architectural challenge, or design decision requiring formal resolution.
- What business or technical requirement triggers this decision?
- What are the constraints, operational environments (SaaS vs Customer-Hosted), or scalability targets?
- What existing systems or interfaces are affected?

---

## 2. Decision Drivers

List the governing forces and considerations that influenced the decision:
1. Architectural alignment (e.g. Principle P-01 Modularity, P-04 Multi-tenant isolation).
2. Operational simplicity and dual-model binary portability (P-08).
3. Performance budgets (e.g. diner read response under 1.5 seconds).
4. Maintainability, security posture, and developer ergonomics.

---

## 3. Considered Options

Detail the viable technical approaches evaluated:
* **Option 1:** [Description, Pros, Cons]
* **Option 2:** [Description, Pros, Cons]
* **Option 3:** [Description, Pros, Cons]

---

## 4. Decision & Rationale

State clearly and unambiguously what was decided and why:
> **Decision:** We choose [Option X] because [rationale].

---

## 5. Consequences & Implications

### 5.1 Positive Impacts
- What becomes easier, faster, safer, or more scalable?

### 5.2 Negative Impacts & Trade-offs
- What complexity, operational overhead, or limitations are introduced?

### 5.3 Risks & Mitigations
- **Risk:** [Potential failure mode or risk]
  - **Mitigation:** [Concrete architectural control or automated test]

---

## 6. Architecture Compliance & Traceability

- **Governing Principles:** [e.g., P-01, P-02, P-04, P-07]
- **Architectural Constraints:** [e.g., CON-01, CON-04, CON-10]
- **Enforcement Test ID:** [e.g., TC-ARC02-01, MOD-001, SEC-002]
- **Supersedes:** [None / ADR-YYYY]
- **Superseded By:** [None / ADR-ZZZZ]
