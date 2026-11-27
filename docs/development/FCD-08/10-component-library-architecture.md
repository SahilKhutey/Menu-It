# FCD-08 §10 — Component Library Architecture

## 1. Architectural Patterns

The Menu-It UI component library (`packages/ui`) is built according to four core architectural patterns:

### 1.1 Unstyled Compound Structure
Complex components (such as `Card`, `Table`, `Dialog`, `Tabs`) are implemented using the **Compound Component Pattern**:
```tsx
<Card>
  <CardHeader>
    <CardTitle>Menu Item</CardTitle>
  </CardHeader>
  <CardContent>Description here...</CardContent>
</Card>
```
This pattern provides clear visual hierarchy, composability, and clean prop delegating.

### 1.2 Strict CSS Class Namespacing
To avoid CSS class collisions between monorepo packages and third-party libraries, all component classes are namespaced with the `menu-it-` prefix:
- `.menu-it-button`
- `.menu-it-input`
- `.menu-it-card`
- `.menu-it-badge`
- `.menu-it-dialog`
- `.menu-it-tabs`
- `.menu-it-skeleton`
- `.menu-it-empty-state`

Layout primitives use `.ui-container`, `.ui-grid`, and `.ui-stack`.

### 1.3 Polymorphic and Accessible Forms
Input elements automatically generate accessible label associations using React's `useId()` hook:
```tsx
const generatedId = useId();
const inputId = id || generatedId;
// <label htmlFor={inputId}>
// <input id={inputId} aria-describedby={error ? `${inputId}-error` : undefined}>
```
When an error is passed, the input automatically sets `aria-invalid="true"` and associates the error message using `aria-describedby`.

### 1.4 Controlled Dialog & Tabs Semantics
- `<Dialog>` manages focus traps, prevents document background scrolling (`overflow: hidden`), attaches `role="dialog"`, `aria-modal="true"`, and handles `Escape` key listeners.
- `<Tabs>` assigns `role="tablist"`, `role="tab"`, and `role="tabpanel"` with matching `aria-controls` and `aria-labelledby` attributes.
