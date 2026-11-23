# 33 — Traceability Matrix
**ARC-11: Infrastructure & Deployment Architecture**

## End-to-End Requirement Traceability
| Invariant / Requirement | Work Package | Architecture Decision | Test Scenario | Operational Runbook |
| :--- | :--- | :--- | :--- | :--- |
| **ARC11-I01 (Codebase Unification)** | WP-ARC11-01 | ADR-0193 | T001, T025, T111 | `CUSTOMER_HOSTED_INSTALLATION.md` |
| **ARC11-I02 (Non-Root Privilege)** | WP-ARC11-02 | ADR-0194 | T014 | `SECURITY_OPERATIONS.md` |
| **ARC11-I03 (Ephemeral Redis)** | WP-ARC11-04 | ADR-0196 | T033, T034, T114 | `CACHE_FAILURE.md` |
| **ARC11-I04 (Database Isolation)** | WP-ARC11-04 | ADR-0208 | T031, T032 | `DATABASE_OPERATIONS.md` |
| **ARC11-I05 (Zero-Downtime Migration)**| WP-ARC11-08 | ADR-0197 | T061–T065 | `FAILED_MIGRATION.md` |
| **ARC11-I06 (Pre-Migration Backup)** | WP-ARC11-08 | ADR-0200 | T066 | `DATABASE_BACKUP.md` |
| **ARC11-I07 (Secret Redaction)** | WP-ARC11-07 | ADR-0203 | T010, T116 | `INCIDENT_RESPONSE.md` |
| **ARC11-I08 (Strict Preflight)** | WP-ARC11-07 | ADR-0202 | T001–T009 | `PRODUCTION_DEPLOYMENT.md` |
| **ARC11-I09 (Storage Traversal Guard)**| WP-ARC11-10 | ADR-0210 | T075 | `STORAGE_OPERATIONS.md` |
| **ARC11-I10 (Tenant Job Context)** | WP-ARC11-09 | ADR-0199 | T083 | `WORKER_OPERATIONS.md` |
| **ARC11-I11 (Immutable Tagging)** | WP-ARC11-13 | ADR-0193 | T025, T091 | `RELEASE_CHECKLIST.md` |
| **ARC11-I12 (Health Probe Separation)**| WP-ARC11-11 | ADR-0201 | T049–T051 | `API_UNAVAILABLE.md` |
| **ARC11-I13 (Deterministic Backup)** | WP-ARC11-12 | ADR-0211 | T096–T105 | `BACKUP_POLICY.md` |
| **ARC11-I14 (Customer Self-Sufficiency)| WP-ARC11-05 | ADR-0214 | T110–T115 | `CUSTOMER_HOSTED_INSTALLATION.md` |
| **ARC11-I15 (Frontend Bundle Budget)** | WP-ARC11-02 | ADR-0204 | T011 | `RELEASE_CHECKLIST.md` |\n