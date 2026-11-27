# FCD-07 §09 — Pagination, Filtering & Sorting Standards

## 1. Pagination Standards

Menu-It implements offset-limit pagination wrapped in a consistent metadata envelope.

### Request Contract
- `page`: 1-indexed integer (`default=1`, `ge=1`).
- `page_size`: Number of items per page (`default=20`, `ge=1`, `le=100`).
- Derived: `offset = (page - 1) * page_size`.

### Response Contract (`PaginationMeta`)
```json
{
  "page": 1,
  "page_size": 20,
  "total_items": 45,
  "total_pages": 3,
  "has_next": true,
  "has_previous": false
}
```

---

## 2. Filtering Standards

- Filter fields are passed as explicit query parameters:
  - `status=active`
  - `timezone=America/New_York`
- In-memory and SQL filters apply strictly within tenant boundaries.

---

## 3. Sorting Standards & SQL Injection Prevention

- Sort parameters use the format `sort=field:direction` (e.g. `sort=created_at:desc`).
- Field names are checked against a strict domain whitelist per repository.
- Unknown sort columns are rejected with `422 Unprocessable Entity` rather than passed dynamically to the SQL builder.
