# FCD-08 §06 — Spacing and Layout System

## 1. 4px Grid Foundation

All spatial measurements (margins, paddings, gaps, and component heights) in Menu-It adhere strictly to a **4-pixel incremental grid**.
This consistency prevents visual jitter, aligns horizontal baselines, and simplifies responsive reflow across viewport changes.

---

## 2. Layout Components

Menu-It provides three dedicated layout primitives in `@menu-it/ui`:

### 2.1 Container (`<Container>`)
Constrains horizontal content width and centers layout across viewport sizes with fluid gutters.
- **Sizes:**
  - `sm`: Max width `640px` (single-column forms, auth cards).
  - `md`: Max width `768px` (articles, settings forms).
  - `lg`: Max width `1024px` (restaurant menus, standard admin views).
  - `xl`: Max width `1280px` (complex dashboards, analytics tables).
  - `full`: Max width `100%` (fluid full-bleed layouts).

### 2.2 Grid (`<Grid>`)
Declarative CSS Grid container supporting responsive column counts and standard token gaps:
- **Columns:** `1`, `2`, `3`, `4`, `6`, `12`.
- **Responsive Columns:** `columns={{ sm: 1, md: 2, lg: 3, xl: 4 }}`.
- **Gaps:** `none` (0), `xs` (4px), `sm` (8px), `md` (16px), `lg` (24px), `xl` (32px).

### 2.3 Stack (`<Stack>`)
Declarative flexbox container for arranging child elements along a vertical or horizontal axis:
- **Direction:** `vertical` (column) or `horizontal` (row).
- **Alignment:** `start`, `center`, `end`, `stretch`.
- **Gaps:** `none`, `xs`, `sm`, `md`, `lg`, `xl`.
- **Wrap:** Boolean toggle for flex wrapping.

---

## 3. Safe-Area Inset Handling

Mobile devices with screen notches, rounded display corners, or dynamic home bars require protected safe areas. Menu-It layout components incorporate CSS `env(safe-area-inset-*)`:

```css
.app-header {
  padding-top: max(12px, env(safe-area-inset-top));
  padding-left: max(5%, env(safe-area-inset-left));
  padding-right: max(5%, env(safe-area-inset-right));
}

.app-footer {
  padding-bottom: max(18px, env(safe-area-inset-bottom));
}
```
This guarantees touch targets remain accessible on iOS Safari and Android edge-to-edge browsers.
