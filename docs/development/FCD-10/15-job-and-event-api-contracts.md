# FCD-10 — Job & Event API Contracts

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Internal Management API Specification

Mounted under `/api/v1/internal`:

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/internal/jobs` | Submit permitted background job | `202 Accepted` |
| `GET` | `/api/v1/internal/jobs/{id}` | Inspect job execution status | `200 OK` |
| `POST` | `/api/v1/internal/jobs/{id}/cancel` | Cancel queued job | `200 OK` |
| `GET` | `/api/v1/internal/dead-letters` | List tenant-scoped dead letters | `200 OK` |
| `GET` | `/api/v1/internal/dead-letters/{id}` | Inspect failure details | `200 OK` |
| `POST` | `/api/v1/internal/dead-letters/{id}/replay`| Authorized replay of failed job | `200 OK` |

---

## 2. Response Envelope

All endpoints strictly adhere to the universal FCD-07 `APIResponse[T]` envelope with `request_id` and UTC `timestamp`.
