# ARC-08 §12 — Optimistic Concurrency & Versioning

## 1. Concurrency Protocol
To eliminate lost updates when multiple managers edit a menu simultaneously:
1. Every read (`GET /menus/{menu_id}/customization`) returns an `ETag` header:
   `ETag: "revision-3"`
2. Every write (`PUT /menus/{menu_id}/customization`) must supply an `If-Match` header matching the current revision:
   `If-Match: "revision-3"`
3. If the server revision has changed, the update is rejected immediately with HTTP 409 Conflict:
   ```json
   {
     "type": "about:blank",
     "title": "Conflict",
     "status": 409,
     "code": "VERSION_CONFLICT",
     "detail": "Concurrency conflict: Draft is at revision 4, but expected revision was 3."
   }
   ```
4. On success, the server increments revision to 4, updates `ETag: "revision-4"`, and creates an immutable snapshot in `customization_revisions`.
