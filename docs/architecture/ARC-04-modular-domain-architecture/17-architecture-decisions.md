# 17 — Architectural Decision Records Baseline

**Specification:** ARC-04 §19  
**Project:** ModularMenu  

---

## 1. ARC-04 Architectural Decisions Baseline (ADR-0028 to ADR-0043)

| Decision ID | Decision Title | Status | Governing ADR |
| :--- | :--- | :--- | :--- |
| **ARC04-D01** | Modular monolith with explicit domain boundaries | **Accepted** | ADR-0028 |
| **ARC04-D02** | Sixteen logical business modules inventory | **Accepted** | ADR-0029 |
| **ARC04-D03** | Each business concept has one authoritative owner | **Accepted** | ADR-0030 |
| **ARC04-D04** | Domain code independent of framework and infrastructure | **Accepted** | ADR-0031 |
| **ARC04-D05** | Modules communicate exclusively through public contracts | **Accepted** | ADR-0032 |
| **ARC04-D06** | No direct cross-module ORM access or model imports | **Accepted** | ADR-0033 |
| **ARC04-D07** | Aggregate boundaries enforce business consistency | **Accepted** | ADR-0034 |
| **ARC04-D08** | Domain events represent completed business facts | **Accepted** | ADR-0035 |
| **ARC04-D09** | In-process communication is the default | **Accepted** | ADR-0036 |
| **ARC04-D10** | Transactional outbox only for high-reliability requirements| **Accepted** | ADR-0037 |
| **ARC04-D11** | Theme, layout, and component configs are schema-versioned | **Accepted** | ADR-0038 |
| **ARC04-D12** | Visual editor maintains independent draft revisions | **Accepted** | ADR-0039 |
| **ARC04-D13** | Publishing produces immutable SHA-256 snapshots | **Accepted** | ADR-0040 |
| **ARC04-D14** | Renderer does not depend on editor internal state | **Accepted** | ADR-0041 |
| **ARC04-D15** | Optional modules must not break core menu operations | **Accepted** | ADR-0042 |
| **ARC04-D16** | SaaS and self-hosted deployments share identical domain logic| **Accepted** | ADR-0043 |

---

## 2. Decision Handoffs to Subsequent Architecture Documents
- **Organization & Tenant Isolation Details:** Reserved for **ARC-05**.
- **Physical Database Schema, Keys, Indexes & RLS:** Reserved for **ARC-06**.
- **Public REST API Specifications & Error Mapping:** Reserved for **ARC-07**.
- **Theme Schemas & Customization Engine:** Reserved for **ARC-08**.
- **Menu Rendering Pipeline & Responsive Output:** Reserved for **ARC-09**.
- **Snapshot & Rollback Consistency Implementation:** Reserved for **ARC-10**.
- **Deployment-Specific Adapters (SaaS vs Appliance):** Reserved for **ARC-11**.
- **Security Policies & Reliability Controls:** Reserved for **ARC-12**.
