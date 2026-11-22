# ARC-09 §11 — Validation & Error Boundaries

## 1. Validation Engine
`RenderInputValidator` verifies rendering readiness before publication or preview generation:
- Checks negative prices (`RENDER_PRICE_INVALID`).
- Validates currency symbols and codes.
- Verifies registered component identifiers in layout slots.
- Warns if recommended theme tokens or food descriptions/images are missing.

## 2. React Error Boundaries
The presentation UI wraps the entire menu in `MenuRenderErrorBoundary`:
- Catches rendering exceptions in individual components.
- Logs telemetry without bubbling errors to the browser window.
- Renders an inline fallback message for affected sections while preserving navigation and the rest of the menu.
