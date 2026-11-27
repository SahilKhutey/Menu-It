# FCD-09 §13 — Application Logging Standards

## 1. Logging Principles

- **Structured:** Production logs output machine-readable JSON records.
- **Contextual:** Every log record carries correlation identifiers (`request_id`, `correlation_id`, `organization_id`, `user_id`).
- **Secure:** Credentials, passwords, cookies, and secret keys are automatically redacted.
- **Standard Levels:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

---

## 2. Structured JSON Output

The `JsonFormatter` formats records as JSON objects:

```json
{
  "timestamp": "2026-11-25T10:00:00.000000Z",
  "level": "INFO",
  "logger": "menu_it.platform.files",
  "message": "File uploaded successfully",
  "request_id": "req-999",
  "organization_id": "org-777",
  "extra": {
    "filename": "menu.pdf",
    "size_bytes": 1048576
  }
}
```

---

## 3. Context Logger Adapter

Modules obtain a logger bound to trusted context via `get_context_logger()`:
```python
logger = get_context_logger("menu_it.orders", request_id="req-123", organization_id="org-456")
logger.info("Order processed")
```
