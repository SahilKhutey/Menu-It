# Publishing REST API Reference (ARC-10 & ARC-07)

## Base Path: `/api/v1`

### 1. Validate Draft
`POST /menus/{menu_id}/validate`
- Request: `{ "draft_revision": 1 }`
- Response: `ValidationReport` with diagnostics and errors.

### 2. Readiness Check
`GET /menus/{menu_id}/publication-readiness`
- Response: `{ "ready": true, "result": "PASSED", ... }`

### 3. Publish Menu
`POST /menus/{menu_id}/publish`
- Headers: `Idempotency-Key: <UUID>`, `If-Match: "draft-revision-1"`
- Response: `PublishResponse` with `version_number`, `checksum`, `public_url`.

### 4. List Publications
`GET /menus/{menu_id}/publications`
- Response: Array of `PublicationSummary` records.

### 5. Rollback Publication
`POST /menus/{menu_id}/publications/{pub_id}/rollback`
- Request: `{ "target_publication_id": "<UUID>", "reason": "..." }`
- Response: `{ "status": "success", "active_version_id": "<UUID>" }`
