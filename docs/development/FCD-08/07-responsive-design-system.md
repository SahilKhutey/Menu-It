# FCD-08 §07 — Responsive Design System

## 1. Breakpoint Philosophy

Menu-It adheres to a **mobile-first responsive design philosophy**. CSS rules are structured with `min-width` media queries, establishing baseline ergonomics for smartphone touchscreens before layering enhancements for tablet and desktop viewports.

---

## 2. Breakpoint Matrix

| Identifier | Min Width | Target Viewport Range | Primary Layout Adaptations |
| :--- | :--- | :--- | :--- |
| **Mobile (Base)** | `< 640px` | `320px – 639px` | Single-column cards, full-width buttons, collapsible hamburger navigation, bottom-docked actions |
| **Tablet (`sm`)** | `640px` | `640px – 767px` | 2-column menu grids, expanded navigation labels, side-by-side action buttons |
| **Tablet Landscape (`md`)**| `768px` | `768px – 1023px`| 2- to 3-column product grids, persistent filter bars, visible secondary actions |
| **Desktop (`lg`)** | `1024px` | `1024px – 1279px`| Full top navigation, persistent admin sidebars, multi-column analytics dashboards |
| **Wide Desktop (`xl`)** | `1280px` | `1280px+` | 4-column item grids, dual-pane order management, wide table data views |

---

## 3. Touch Targets & Interaction Areas

For handheld devices, touch ergonomics govern interactive component sizing:
- **Minimum Target Dimension:** 44×44 CSS pixels (WCAG 2.5.8 Target Size).
- **Minimum Touch Spacing:** 8px clearance between adjacent interactive elements.
- **Form Inputs:** Minimum height of 42px (sm) to 48px (md/lg) with font sizes >= 16px to prevent automatic mobile Safari viewport zooming on focus.

---

## 4. Reduced Motion Support

Menu-It includes built-in respect for user accessibility preferences regarding system animations:
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```
All shimmer effects, modal transitions, and accordion animations collapse instantaneously when reduced motion is detected.
