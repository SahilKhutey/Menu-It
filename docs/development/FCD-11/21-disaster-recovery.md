# FCD-11 · Document 21: Disaster Recovery, Business Continuity & RPO/RTO Validation

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Disaster Recovery (DR) Tiers

Menu-It defines four catastrophic disaster scenarios:

| Scenario | Severity | Trigger | Recovery Strategy |
| :--- | :--- | :--- | :--- |
| **Zone Outage** | Level 1 | Availability zone network or hardware failure | Multi-AZ deployment automatically routes traffic to surviving zone; zero human intervention. |
| **Region Outage** | Level 2 | Complete primary cloud region offline | DNS failover to standby secondary region; restore latest WAL archive; target RTO < 4h. |
| **Data Corruption** | Level 3 | Malicious or buggy script corrupts tenant tables | Point-in-Time Recovery (PITR) rollback to the exact timestamp before corruption occurred. |
| **Ransomware / Host Loss** | Level 4 | Compromise of production infrastructure | Wipe environment; deploy clean infrastructure via Terraform/GitOps; restore from air-gapped immutable backup. |

---

## 2. Annual DR Game Day Validation

- Twice annually, the engineering team executes a simulated regional failover exercise ("DR Game Day").
- The exercise validates that backup archives can be restored within the 4-hour RTO and data consistency matches the 15-minute RPO.
