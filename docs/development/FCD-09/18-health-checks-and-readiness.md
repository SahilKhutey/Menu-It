# FCD-09 §18 — Health Checks & Operational Readiness

## 1. Probes Matrix

| Probe | Endpoint | Status Semantics | Criticality |
| :--- | :--- | :--- | :--- |
| **Liveness** | `GET /api/v1/health/live` | `200 alive` | Process responsive |
| **Health** | `GET /api/v1/health` | `200 healthy` + metadata | Basic operational health |
| **Readiness** | `GET /api/v1/health/ready`| `200 ready` / `503 unavailable` | Ready to accept traffic |
| **Platform** | `GET /api/v1/health/platform`| Aggregated component diagnostics | Subsystem health status |

---

## 2. Subsystem Health Checks

- **Database Check:** Verifies PostgreSQL connectivity via a lightweight `SELECT 1` query.
- **Storage Check:** Verifies accessibility of the storage root directory.
- **Notifications Check:** Verifies email provider configuration and operational status.

No internal filesystem paths, database credentials, or secret keys are exposed in health responses.
