# ARC-09 §13 — API & HTTP Specifications

## 1. Registered Endpoints

| Method | Path | Auth Required | Cache Control | Response DTO |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/public/restaurants/{restaurant_slug}/menus/{menu_slug}/render` | No (Anonymous) | `public, max-age=60, s-maxage=300` | `PublicMenuRenderResponse` |
| `POST` | `/api/v1/restaurants/{restaurant_id}/menus/{menu_id}/preview` | Yes (Bearer JWT) | `private, no-cache, no-store` | `DraftPreviewResponse` |
| `POST` | `/api/v1/restaurants/{restaurant_id}/menus/{menu_id}/render-validation` | Yes (Bearer JWT) | `no-store` | `RenderValidationResponse` |
| `GET` | `/api/v1/public/restaurants/{restaurant_slug}/menus/{menu_slug}/metadata` | No (Anonymous) | `public, max-age=300` | `PublicMetadataOut` |

## 2. HTTP Status Codes
- `200 OK`: Successful menu render delivery.
- `304 Not Modified`: Cached ETag match on conditional GET.
- `401 Unauthorized`: Unauthenticated request on draft preview.
- `403 Forbidden`: Cross-tenant operator on draft preview.
- `404 Not Found`: Nonexistent restaurant slug, menu slug, or unpublished draft.
- `422 Unprocessable Entity`: Invalid request payload syntax.
