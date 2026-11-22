# ARC-09 §20 — WCAG Accessibility & Screen Readers

## 1. Compliance Baseline
ModularMenu digital menus comply with WCAG 2.1 Level AA accessibility requirements.

## 2. Accessibility Invariants
1. **Semantic Heading Hierarchy**: H1 for Restaurant, H2 for Categories, H3 for Items (`ARC09-T093`).
2. **Accessible Item Cards**: ARIA labels combine dish name, dietary classification, and formatted price (`ARC09-T095`).
3. **Out-of-Stock Indication**: Unavailable items are clearly marked visually and programmatically with `aria-disabled="true"` (`ARC09-T096`).
4. **Touch Target Dimensions**: Navigation pills, buttons, and clickable items meet the minimum 44x44px touch target guidelines (`ARC09-T099`).
5. **Color Contrast**: Surface and text tokens maintain a contrast ratio exceeding 4.5:1 (`ARC09-T098`).
6. **Focus Visible Outlines**: Keyboard navigation (Tab, Enter, Space) is supported with visible focus rings (`ARC09-T106`).
