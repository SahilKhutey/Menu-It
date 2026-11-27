# FCD-10 — Cache Policies & Invalidation Rules

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Standard TTL Taxonomy

| Category | TTL | Constant | Invalidation Trigger |
| :--- | :--- | :--- | :--- |
| **Short-Lived / Dynamic** | 60s | `TTL_SHORT` | Order status changes, table availability |
| **Medium / Catalogs** | 300s | `TTL_MEDIUM` | Menu item updates, category reordering |
| **Long / Static Profiles** | 600s | `TTL_LONG` | Restaurant profile updates, operating hours |
| **Very Long / Tenant Config**| 3600s | `TTL_VERY_LONG` | Brand customization, system defaults |

---

## 2. Cache-Aside & Failure Guarantees

- **Cache-Aside Flow:** Check cache -> on miss, query repository -> serialize and cache -> return result.
- **Fail-Open Policy:** A cache outage degrades response times but does NOT cause API errors. Data correctness is guaranteed by PostgreSQL.
- **Security Invariant:** Tenant-private data is never returned without prior authenticated tenant resolution.
