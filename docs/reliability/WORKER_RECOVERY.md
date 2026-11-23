# Background Worker Resilience & DLQ Guide
**ModularMenu · Reliability & SRE Guides · Version 1.0**
**Approved Operational Specification**

---

## Document Control
| Attribute | Definition |
| :--- | :--- |
| **Document ID** | WORKER_RECOVERY |
| **Title** | Background Worker Resilience & DLQ Guide |
| **Category** | Reliability & SRE Guides |
| **Status** | Active Operational Standard |
| **Enforcement** | Automated CI/CD Gates, Production Monitoring, Architecture Invariants |

---

## 1. Objective & Scope
Outbox poller crash recovery, state preservation, poison pill routing to dead-letter queue, and queue monitoring.

ModularMenu enforces strict compliance with this standard across both the **Managed SaaS** and **Customer-Hosted** deployment editions. Any deviation requires formal review under the Security Exception Policy.

---

## 2. Core Policies & Requirements

### 2.1 Foundational Invariants
- **Non-Negotiable:** All operational activities, automated services, and software modules must adhere to the ARC-12 Architecture Specification.
- **Fail-Closed Principle:** When encountering ambiguous states or service degradation, components must fail closed to protect tenant boundaries and data confidentiality.
- **Continuous Audit:** All actions executed under this policy must emit structured audit events.

### 2.2 Technical Requirements & Rules
1. **Implementation Guardrails:** Configuration must be managed through declarative manifests (`infrastructure/security/manifests/`, `infrastructure/reliability/manifests/`).
2. **Access & Privilege:** Actions requiring administrative authority must adhere strictly to the principle of least privilege.
3. **Telemetry & Monitoring:** Observability metrics must track policy compliance, alerting operations teams if defined thresholds are breached.

---

## 3. Standard Operating Procedures (SOP)

### 3.1 Verification & Execution
- **Step 1:** Verify system preconditions and relevant tenant context.
- **Step 2:** Execute designated operational procedure using documented CLI tools or automated scripts.
- **Step 3:** Inspect logs and telemetry to ensure zero errors or context leakage.
- **Step 4:** Record completion status in the operational audit register.

### 3.2 Automated Validation
This policy is validated continuously against the 150 automated test scenarios in `tests/security/test_arc12_security_catalogue.py`.

---

## 4. Revision & Audit History
- **Version 1.0:** Initial baseline established under ARC-12 Security, Scalability & Reliability Architecture.
