# 10. Pagination, Filtering, and Search

## 1. Pagination Standard
- Default cursor-based pagination using base64-encoded cursor tokens.
- Query parameters: `limit` (default 50, maximum 100), `cursor` (opaque string).
- Response includes `pagination` metadata object with `has_next_page` and `next_cursor`.
