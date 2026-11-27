# FCD-07 §04 — Schemas, Serialization & Error Envelopes

## 1. Universal Response Envelope

All API endpoints return responses serialized using the generic `APIResponse[T]` model:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
    "timestamp": "2026-11-24T05:40:00Z"
  }
}
```

When an error occurs, `data` is `null`, and `error` is populated:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "RESOURCE_CONFLICT",
    "message": "Restaurant with slug 'bistro-central' already exists in this organization.",
    "details": []
  },
  "meta": {
    "request_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
    "timestamp": "2026-11-24T05:40:00Z"
  }
}
```

---

## 2. Standardized Error Detail Contract

Validation errors produce structured field-level diagnostic items in `details`:

```json
{
  "field": "name",
  "code": "string_too_short",
  "message": "String should have at least 1 character"
}
```

Crucially, raw invalid values (e.g. attempted passwords, internal API tokens) are strictly stripped during normalization in `normalize_validation_error()` to prevent data leakage.

---

## 3. Strict Serialization Invariants

- **Numeric Representation:** All currency amounts are serialized as string decimal representations (e.g. `"14.50"`) accompanied by a 3-letter ISO-4217 currency code. Floating point serialization is prohibited.
- **Date & Time:** All timestamps are formatted as ISO 8601 strings in UTC (`YYYY-MM-DDTHH:MM:SSZ`).
- **Identifiers:** All IDs are standard UUID v4 strings.
