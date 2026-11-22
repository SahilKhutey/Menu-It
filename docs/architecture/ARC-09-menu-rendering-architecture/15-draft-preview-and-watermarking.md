# ARC-09 §15 — Draft Preview & Watermarking

## 1. Operator Preview Experience
Restaurant operators can preview changes in real time before publishing to guests.
- Route: `/app/menus/[menuId]/preview`
- Endpoint: `POST /api/v1/restaurants/{restaurant_id}/menus/{menu_id}/preview`

## 2. Preview Safeguards
1. **Prominent Watermark**: A high-visibility banner fixed at the top of the viewport: `"PREVIEW MODE — Unpublished Draft"`.
2. **Metadata Flags**: `is_preview: true`, `watermark_text: "PREVIEW - UNPUBLISHED DRAFT"`.
3. **No-Store Caching**: Strict `Cache-Control: private, no-store, no-cache` prevents browser or proxy caching of draft content.
4. **Actionable Warnings**: Missing photos or descriptions are surfaced in a diagnostic panel to aid menu completion.
