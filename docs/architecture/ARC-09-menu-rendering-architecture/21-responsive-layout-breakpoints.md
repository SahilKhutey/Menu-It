# ARC-09 §21 — Responsive Layout Breakpoints

## 1. Breakpoint Definitions
The rendering engine adapts seamlessly across viewport sizes:
- **Mobile (`0px - 639px`)**: Single column layout, touch-optimized sticky horizontal pill navigation, compressed card spacing.
- **Tablet (`640px - 1023px`)**: 2-column card grid, sidebar navigation or sticky pills, expanded descriptions.
- **Desktop (`1024px+`)**: 3-column card grid, multi-column categories, full imagery and sidebar filters.

## 2. Dynamic Viewport Meta
```html
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5">
```
Ensures user-initiated pinch-to-zoom is supported for visually impaired diners while preventing horizontal overflow.
