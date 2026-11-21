# 05. API Error Handling Architecture

## 1. RFC 7807 / RFC 9457 Specification
All error responses strictly follow the Problem Details specification:
```json
{
  "type": "https://api.modularmenu.in/errors/resource-not-found",
  "title": "Resource Not Found",
  "status": 404,
  "code": "RESOURCE_NOT_FOUND",
  "detail": "Menu with ID '123e4567-e89b-12d3-a456-426614174000' not found",
  "instance": "/api/v1/menus/123e4567-e89b-12d3-a456-426614174000",
  "request_id": "c1f7b8a2-9b2e-4b45-a745-f938dcb904a1",
  "timestamp": "2026-11-21T09:00:00Z",
  "invalid_params": []
}
```

## 2. Centralized Error Registry
Defined in `backend/architecture/error_codes.yaml`:
- `VALIDATION_ERROR` (422)
- `AUTHENTICATION_REQUIRED` (401)
- `PERMISSION_DENIED` (403)
- `RESOURCE_NOT_FOUND` (404)
- `CONFLICT` (409)
- `CONCURRENCY_CONFLICT` (409)
- `IDEMPOTENCY_CONFLICT` (409)
- `RATE_LIMIT_EXCEEDED` (429)
- `UPLOAD_TOO_LARGE` (413)
- `UNSUPPORTED_MEDIA_TYPE` (415)
- `DEPENDENCY_UNAVAILABLE` (503)
- `INTERNAL_SERVER_ERROR` (500)
