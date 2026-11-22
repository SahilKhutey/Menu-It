# ARC-09 §03 — Rendering Modes & Execution Context

## 1. Supported Rendering Modes
ModularMenu supports three distinct rendering execution modes:

| Mode | Target User | Security Context | Caching Policy | Watermarking |
| :--- | :--- | :--- | :--- | :--- |
| **`public_published`** | Anonymous dining guests | No authentication required; read-only | `Cache-Control: public, max-age=60, s-maxage=300`, ETag | None |
| **`draft_preview`** | Authenticated restaurant staff | JWT required (`verify_restaurant_access`) | `Cache-Control: private, no-store` | Visual banner & `is_preview: true` |
| **`local_editor`** | Browser visual menu designer | In-memory React state | Zero network caching | Live canvas outlines |

## 2. Security Boundaries Between Modes
- In `public_published`, unpublished categories and draft menu items are physically omitted from the database query and response payload.
- In `draft_preview`, items missing descriptions or photos trigger structured `warnings` in the metadata payload without blocking rendering.
- Cross-tenant access to draft preview endpoints returns HTTP 403 / 404.
