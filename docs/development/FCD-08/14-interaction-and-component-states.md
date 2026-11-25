# FCD-08 §14 — Interaction & Component States

## 1. Standard Interactive States

Every interactive component across the Menu-It design system implements six consistent lifecycle states:

```mermaid
stateDiagram-v2
    [*] --> Default
    Default --> Hover : Cursor enters
    Hover --> Default : Cursor leaves
    Default --> FocusVisible : Keyboard Tab
    FocusVisible --> Active : Keydown (Space/Enter)
    Hover --> Active : Pointer down
    Active --> Default : Pointer/Key release
    Default --> Disabled : disabled=true
    Default --> Loading : isLoading=true
```

---

## 2. Component State Specifications

### 2.1 Default State
Standard resting visual representation using base semantic tokens:
- Button: `background: var(--primary); color: var(--primary-foreground);`
- Input: `border-color: var(--border); background: var(--background);`

### 2.2 Hover State (`:hover`)
Visual confirmation of cursor presence without causing layout reflow:
- Button: transitions to darker/lighter token (`var(--primary-hover)`).
- Table Rows: subtle background highlight (`var(--muted)`).

### 2.3 Focus-Visible State (`:focus-visible`)
Triggered strictly on keyboard navigation (Tab/Shift+Tab) or programmatic focus:
- Unambiguous 3px solid focus ring in `var(--ring)` with `outline-offset: 2px`.
- Never suppressed via `outline: none` without replacement.

### 2.4 Active / Pressed State (`:active`)
Physical depth feedback upon pointer or keypress down:
- Button: `transform: scale(0.98)` or deeper background shading.

### 2.5 Disabled State (`:disabled` / `aria-disabled="true"`)
Inactive state preventing interaction:
- Visual reduction: `opacity: 0.5`.
- Cursor: `cursor: not-allowed`.
- Pointer events suppressed.

### 2.6 Loading State (`isLoading={true}`)
Asynchronous pending state for buttons and form actions:
- Children hidden or accompanied by an animated SVG spinner.
- Button is automatically disabled to prevent duplicate submissions.
- `aria-busy="true"` announced to assistive technology.
