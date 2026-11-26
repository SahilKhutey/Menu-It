# FCD-12 · Document 05: API Contract & Integration Testing

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. API Envelope Invariant

All Menu-It API endpoints strictly adhere to the universal JSON envelope format defined in FCD-02 and standardized in FCD-07:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "req-98f24b2e-...",
    "timestamp": "2026-11-26T09:45:00.000000Z"
  }
}
```

On validation or server error:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The supplied data is invalid.",
    "details": [
      {
        "field": "email",
        "message": "value is not a valid email address"
      }
    ]
  },
  "meta": {
    "request_id": "req-98f24b2e-...",
    "timestamp": "2026-11-26T09:45:00.000000Z"
  }
}
```

---

## 2. Shared Type Synchronization

- The `@menu-it/shared-types` package mirrors backend Pydantic models.
- Any API schema change must be verified against frontend client types to prevent contract drift during CI execution.
