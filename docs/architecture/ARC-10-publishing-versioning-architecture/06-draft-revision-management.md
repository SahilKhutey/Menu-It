# ARC-10 §6: Draft Revision Management
**Immutable Revisions & Optimistic Concurrency**

## 1. Monotonic Revisioning
Every save action on a menu draft creates an immutable `DraftRevision`:
- Increments `revision_number` monotonically.
- Links `parent_revision_id` to establish edit ancestry.
- Computes canonical SHA-256 content hash of the draft payload.

## 2. Optimistic Concurrency Control
When publishing or saving edits, clients provide:
```http
POST /api/v1/menus/{menu_id}/publish
If-Match: "draft-revision-18"
```
If the draft in the database is at revision 19 (due to a concurrent edit), the server rejects the request with HTTP 409 Conflict (`DRAFT_REVISION_STALE`).
