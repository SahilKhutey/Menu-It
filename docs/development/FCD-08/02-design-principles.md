# FCD-08 §02 — Design Principles

## 1. Core Principles

The Menu-It design system is guided by five foundational principles that inform all architectural and visual decisions.

### 1.1 Multi-Tenant Adaptability Without Compromising Integrity
- The platform supports multiple restaurant brands, each possessing distinct color schemes, typography, and visual aesthetics.
- Dynamic branding is achieved strictly through CSS custom property substitutions governed by the Theme Engine.
- Restaurant themes can never alter layout geometry, break layout bounds, compromise structural responsive behavior, or bypass accessibility gates.

### 1.2 Accessibility as a Non-Negotiable Baseline (WCAG 2.2 AA)
- Visual appeal must never take precedence over readability and usability.
- All text and interactive controls must pass a minimum contrast ratio of 4.5:1 against their adjacent background (3:1 for large graphical elements and large text).
- Every interactive element provides clearly visible keyboard focus indicators (`--ring`) with an explicit outline offset.
- Screen readers receive appropriate semantic markup, landmark regions, and live announcements.

### 1.3 Strict Design Token Discipline
- No component or application may introduce arbitrary hardcoded hex colors, raw pixel paddings, or magic numbers.
- Visual properties must be derived from the design token hierarchy:
  - **Primitive Token:** Raw scale (e.g., `colors.orange[600]`).
  - **Semantic Token:** Intent and role (e.g., `var(--primary)`).
  - **Component Usage:** Applied directly via CSS class (e.g., `background: var(--primary)`).

### 1.4 Mobile-First Responsive Geometry
- Restaurant dining menus and ordering interfaces are predominantly accessed via mobile smartphones (QR scan table-side).
- Layouts are engineered mobile-first (min-width media queries).
- Touch targets on interactive components (buttons, tab triggers, inputs) guarantee a minimum hit area of 44×44px.
- Safe-area insets (`env(safe-area-inset-top)`, `env(safe-area-inset-bottom)`) are accounted for to prevent notch and home-bar clipping.

### 1.5 Minimal Runtime Overhead & Server-Safe Rendering
- Visual foundations rely on standard CSS custom properties and lightweight utility classes rather than heavy CSS-in-JS runtime injection libraries.
- All components are fully compatible with Next.js App Router, React Server Components (RSC), and standard client hydration patterns.
- Zero client-side hydration mismatches occur when switching between light and dark themes.

---

## 2. Design Token Governance Rules

| Rule | Requirement | Enforcement |
| :--- | :--- | :--- |
| **Colors** | Must reference semantic custom properties (`var(--primary)`, `var(--muted)`) | ESLint & code reviews |
| **Contrast** | Normal text >= 4.5:1, large text >= 3.0:1 | Automated theme validation function `validateTheme()` |
| **Spacing** | Multiples of the 4px base grid (4, 8, 12, 16, 20, 24, 32, 48, 64px) | CSS token scales |
| **Typography**| Clamp-based fluid sizing or standard token scales (`--font-size-*`) | Token variables |
| **Border Radii**| Semantic variables (`--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-full`) | Token variables |
| **Focus Rings**| Visible focus ring (`3px solid var(--ring); outline-offset: 2px`) | Applied across all interactive components |
