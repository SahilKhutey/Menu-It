# ARC-08 §23 — Verification & Validation Criteria

## 1. Verification Areas (18 Criteria)
All 18 verification areas (`ARC08-VF01` to `ARC08-VF18`) are formally certified:
- `VF01` (Catalogue Loading): 6 themes, 4 layouts, 13 components verified.
- `VF02` (Token Resolution): Deterministic deep merge and fallback verified.
- `VF03` (CSS Variables): Proper `--mm-` variable generation certified.
- `VF04` (Schema Validation): Rejection of illegal fields and malformed structures verified.
- `VF05` (Optimistic Concurrency): ETag mismatch produces 409 Conflict.
- `VF06` (Security Limits): 256KB, 100 components, depth 10 enforced.
- `VF07` (XSS Prevention): Rejection of `<script>` and executable attributes verified.
- `VF08` (Tenant Isolation): Cross-tenant reads and writes rejected with 404/403.
- `VF09` (Revision History): Immutable revision log and restoration verified.
- `VF10` (Settings Editor): Form editing and color swatch updates verified.
- `VF11` (Visual Editor): Drag-and-drop slots and property changes verified.
- `VF12` (Undo/Redo): 50-step bounded command history verified.
- `VF13` (Ephemeral Preview): Preview without draft persistence verified.
- `VF14` (Public Decoupling): Draft edits do not mutate published snapshots.
- `VF15` (Contrast Compliance): WCAG 2.1 AA text contrast verified.
- `VF16` (Responsive Viewports): 320px, 360px, 768px, 1280px verified.
- `VF17` (Latency Targets): Resolver <5ms, Save <500ms verified.
- `VF18` (Resilience): Cache miss fallback to file manifests verified.

## 2. Product Validation Scenarios (8 Scenarios)
All 8 product validation scenarios (`VAL-01` to `VAL-08`) pass with zero defects.
