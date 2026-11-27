# FCD-11 · Document 25: Service Level Objectives (SLOs), Error Budgets & Operational Review

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Service Level Indicators (SLIs) & Objectives (SLOs)

| Service Area | Indicator (SLI) | Target Objective (SLO) | Measurement Window |
| :--- | :--- | :--- | :--- |
| **API Availability** | Successful responses (`status < 500`) / total valid requests | **99.9%** availability | Rolling 30 days |
| **Read Latency (Public Menu)** | Proportion of requests served under 100ms | **95.0%** < 100ms | Rolling 30 days |
| **Write Latency (Orders & Admin)** | Proportion of requests served under 350ms | **95.0%** < 350ms | Rolling 30 days |
| **Background Processing** | Proportion of outbox events processed under 5.0s | **99.0%** < 5.0s | Rolling 7 days |
| **Data Freshness** | Read replica replication lag under 1.0s | **99.9%** < 1.0s | Rolling 30 days |

---

## 2. Error Budget Management

- An availability SLO of 99.9% allows an error budget of approximately 43.2 minutes of unplanned downtime per 30 days.
- **Budget Burn Rate Actions:**
  - **100% Budget Remaining:** Normal feature delivery.
  - **< 25% Budget Remaining:** Feature releases throttled; priority shifts to reliability and performance remediation.
  - **0% Budget Remaining (Budget Depleted):** Feature freeze enacted; 100% engineering effort dedicated to stability improvements.
