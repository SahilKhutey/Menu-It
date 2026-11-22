# ARC-10 §24: Performance & Scalability
**Latency Budgets & Benchmarking Criteria**

## 1. Performance Budgets
- **Validation Execution:** p95 < 2000 ms.
- **Snapshot Building & Hashing:** p95 < 1000 ms.
- **Synchronous Publish Transaction:** p95 < 3000 ms.
- **Rollback Pointer Shift:** p95 < 1000 ms.
- **Active Lookup Origin:** p95 < 150 ms.
- **Frontend Bundle JS:** First Load JS < 120 kB (Actual: 92 kB).
