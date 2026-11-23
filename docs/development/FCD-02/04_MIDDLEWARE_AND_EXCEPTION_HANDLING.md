# FCD-02 — Middleware & Exception Handling Architecture

## 1. Request ID Middleware (`RequestIDMiddleware`)
Located at `apps/api/src/menu_it/middleware/request_id.py`:
- Inspects incoming `X-Request-ID` header.
- If present and valid UUID, preserves client correlation ID.
- If missing or malformed, generates a new cryptographic UUIDv4.
- Stores `request.state.request_id` for use in logs and exception responses.
- Attaches `X-Request-ID` to all HTTP responses.

## 2. Centralized Exception Handling
Located at `apps/api/src/menu_it/exceptions/handlers.py`:
All API errors are converted into uniform enveloped JSON payloads conforming to RFC 7807 / RFC 9457:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": []
  },
  "meta": {
    "request_id": "f7c8a3e1-9c6a-4a8c-bfe1-2f15c9d1a311",
    "timestamp": "2026-11-23T12:00:00Z"
  }
}
```

### Handler Types
1. **HTTPException (4xx/5xx):** Serializes clean client error details with matching status code.
2. **RequestValidationError (422):** Formats Pydantic validation errors into structured `details` array containing `loc`, `msg`, and `type`.
3. **Unhandled Exception (500):** Sanitizes error output to `"An unexpected server error occurred."` preventing stack trace, database connection string, or internal path leakage to API clients. Full traces are safely emitted to protected server logs tagged with the correlation `request_id`.
