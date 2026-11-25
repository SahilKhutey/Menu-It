# FCD-10 — Retry, Backoff & Error Classification Policy

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Exponential Backoff with Jitter

The delay before attempt $n$ is calculated via `calculate_retry_delay` in `menu_it.platform.jobs.retry`:
$$d_n = \min(d_{\max}, d_0 \times \text{multiplier}^{n-1}) + J$$

- $d_0 = 5\text{ seconds}$ (initial delay)
- $\text{multiplier} = 2$ (doubles delay with each retry)
- $d_{\max} = 900\text{ seconds}$ (15 minutes cap)
- $J$: random jitter fraction $(0 \le J \le 0.1 \times d_{\text{base}})$ preventing thundering herds.

---

## 2. Error Classification Matrix

| Error Type | Classification | Action |
| :--- | :--- | :--- |
| `ConnectionError`, `TimeoutError` | Transient | Retry with backoff |
| HTTP 429 Rate Limit | Transient | Retry with backoff |
| `ValueError`, `TypeError`, `KeyError` | Permanent | Dead-letter immediately |
| Missing Tenant Context | Security | Dead-letter & log security event |
| Max Attempts Exhausted | Terminal | Persist to `dead_letter_jobs` |
