# FCD-09 §08 — File API Contracts

## 1. Endpoints Overview

| Method | Endpoint | Description | Auth Required | Tenant Scoped |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/files` | Upload file | Bearer Token | Optional / Header |
| `GET` | `/api/v1/files/{id}` | Get metadata | Optional (Public) | Optional / Header |
| `GET` | `/api/v1/files/{id}/content` | Stream file content | Optional (Public) | Optional / Header |
| `DELETE`| `/api/v1/files/{id}` | Soft delete file | Bearer Token | Optional / Header |

---

## 2. Enveloped API Responses

### Upload Response (`201 Created`)
```json
{
  "success": true,
  "data": {
    "id": "e4b33534-7ce0-4ce0-b4f0-ec7b6537ad29",
    "filename": "restaurant-logo.png",
    "mime_type": "image/png",
    "size_bytes": 1048576,
    "visibility": "tenant_private",
    "status": "stored",
    "created_at": "2026-11-25T10:00:00Z"
  },
  "error": null,
  "meta": {
    "request_id": "req-789",
    "timestamp": "2026-11-25T10:00:00Z"
  }
}
```

Internal storage keys, filesystem paths, and server secrets are never exposed in response payloads.
