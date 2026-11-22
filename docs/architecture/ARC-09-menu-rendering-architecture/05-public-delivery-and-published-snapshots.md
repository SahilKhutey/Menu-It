# ARC-09 §05 — Public Delivery & Published Snapshots

## 1. Public Delivery Architecture
Public menu delivery is served via:
- Endpoint: `GET /api/v1/public/restaurants/{restaurant_slug}/menus/{menu_slug}/render`
- Web Route: `/r/[slug]/[menuSlug]`

## 2. Immutable Snapshot Resolution
When a public request arrives:
1. The delivery service queries `Restaurant` by `slug` (asserting `status == 'active'`).
2. The service queries `Menu` by `restaurant_id` and `slug`.
3. The service joins `Publication` and `MenuVersion` on `active_version_id` where `status == 'published'`.
4. If no published version exists, HTTP 404 is returned immediately.
5. The immutable `snapshot_data` JSONB column is loaded and transformed via `RenderInputBuilder`.
6. HTTP `ETag` (SHA-256 hash) and `Cache-Control` headers are attached to the response.
7. If the client supplies a matching `If-None-Match` header, HTTP 304 Not Modified is returned without transferring payload bytes.
