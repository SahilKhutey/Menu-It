# FCD-08 §13 — Accessibility Standards & WCAG 2.2 AA Compliance

## 1. Compliance Target

All user interfaces within the Menu-It platform target full compliance with **Web Content Accessibility Guidelines (WCAG) 2.2 Level AA**.

---

## 2. Key Accessibility Implementations

### 2.1 Contrast Requirements
- **Body & Normal Text:** Ratio $\ge 4.5:1$.
- **Large Text ($\ge 18\text{pt}$ or $\ge 14\text{pt}$ bold):** Ratio $\ge 3.0:1$.
- **Interactive UI Components & Focus Rings:** Ratio $\ge 3.0:1$.
- Automated checks are enforced via `meetsContrastAA()` in the theme engine.

### 2.2 Visible Focus Rings
All interactive components (`<Button>`, `<Input>`, `<TabTrigger>`, links) feature high-visibility focus indicators:
```css
:focus-visible {
  outline: 3px solid var(--ring);
  outline-offset: 2px;
}
```
This ensures keyboard users navigating via Tab can unambiguously identify the focused control across all color themes.

### 2.3 Semantic Landmarks & ARIA Roles
| Component | ARIA Role | Attributes Handled |
| :--- | :--- | :--- |
| `<Dialog>` | `role="dialog"` | `aria-modal="true"`, `aria-labelledby`, `aria-describedby` |
| `<Tabs>` | `role="tablist"` | `aria-selected`, `aria-controls` |
| `<Input>` | `role="textbox"` | `aria-invalid`, `aria-describedby` |
| `<EmptyState>` | `role="status"` | Informs screen readers of non-critical state changes |
| `<Skeleton>` | `aria-hidden="true"` | Prevents screen readers from announcing loading placeholders as content |

### 2.4 Keyboard Navigation & Dismissal
- Modals dismiss on `Escape` key press.
- Modals trap focus within the active dialog frame.
- Tab triggers allow keyboard selection via `Space` and `Enter`.
- Form inputs support natural Tab progression and submit on `Enter`.
