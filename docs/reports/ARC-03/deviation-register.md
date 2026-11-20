# ARC-03 Architectural Deviation Register

**Document ID:** DEV-ARC03-01  
**Project:** ModularMenu / Menu-It  
**Governing Specification:** ARC-03 (Application Architecture)  
**Status:** Approved & Formally Verified  
**Audit Date:** 2026-11-20  

---

## 1. Deviation Summary & Status

In accordance with **ARC-02 §2.4 (Architectural Deviation Procedure)** and **ARC-03 §18**, all variations from standard patterns or proposed baselines must be documented, justified, and evaluated for architectural risk.

### Overall Status: **ZERO (0) UNAPPROVED DEVIATIONS**

| Deviation ID | Category | Description | Justification & Risk Assessment | Approval Status |
| :--- | :--- | :--- | :--- | :--- |
| **DEV-03-001** | Architecture Pattern | Modular Monolith instead of Microservices | Avoids premature distributed systems overhead; enforces in-process boundaries that allow microservice extraction later if warranted. | **APPROVED (ADR-0013)** |
| **DEV-03-002** | Caching Strategy | Optional Redis with In-Memory TTL Fallback | Enables lightweight appliance deployment for customer-hosted restaurants while scaling via Redis in cloud SaaS. | **APPROVED (ADR-0025)** |
| **DEV-03-003** | Testing Strategy | Python AST Import Traversal for Architecture Tests | Provides fast, zero-dependency CI checks on every commit without needing external commercial linting tools. | **APPROVED (ADR-0027)** |

---

## 2. Unapproved Deviations Log

None. No unauthorized architectural departures, unvetted dependencies, or boundary violations exist in the codebase.
