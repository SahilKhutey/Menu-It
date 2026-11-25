# FCD-08 §03 — Design Token Specification

## 1. Token Taxonomy

Design tokens in Menu-It are structured into two distinct tiers: **Primitive Tokens** and **Semantic Tokens**.

```mermaid
graph LR
    P[Primitive Scale: orange.600 = #ea580c] --> S[Semantic Token: --primary = #ea580c]
    S --> C[Component: .ui-button--primary { background: var(--primary); }]
```

---

## 2. Primitive Scales

### 2.1 Spacing Scale (4px Base Grid)
| Token Name | Value | Rem Equivalent | Common Usage |
| :--- | :--- | :--- | :--- |
| `--space-0` | `0px` | `0rem` | Reset |
| `--space-1` | `4px` | `0.25rem` | Micro spacing, badge internal padding |
| `--space-2` | `8px` | `0.5rem` | Tight gap, button horizontal padding (sm) |
| `--space-3` | `12px` | `0.75rem` | Component padding, icon gaps |
| `--space-4` | `16px` | `1rem` | Standard body padding, form row gap |
| `--space-5` | `20px` | `1.25rem` | Intermediate container padding |
| `--space-6` | `24px` | `1.5rem` | Card padding, section spacing |
| `--space-8` | `32px` | `2rem` | Grid gutter, header padding |
| `--space-10` | `40px` | `2.5rem` | Large section separators |
| `--space-12` | `48px` | `3rem` | Hero block spacing |
| `--space-16` | `64px` | `4rem` | Page footer / top-level margins |
| `--space-20` | `80px` | `5rem` | Hero header top space |

### 2.2 Border Radius Scale
| Token Name | Value | Purpose |
| :--- | :--- | :--- |
| `--radius-none` | `0px` | Sharp corners |
| `--radius-sm` | `0.25rem` (4px) | Small badges, code chips, text inputs |
| `--radius-md` | `0.375rem` (6px) | Standard buttons, dialog headers |
| `--radius-lg` | `0.5rem` (8px) | Cards, modals, popovers |
| `--radius-xl` | `0.75rem` (12px) | Large feature cards |
| `--radius-2xl` | `1rem` (16px) | Floating action banners |
| `--radius-full` | `9999px` | Avatars, pills, primary rounded CTAs |

### 2.3 Elevation & Shadow Scale
| Token Name | Value | Usage |
| :--- | :--- | :--- |
| `--shadow-sm` | `0 1px 2px 0 rgba(0, 0, 0, 0.05)` | Input fields, table row hover |
| `--shadow-md` | `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)` | Cards, dropdown menus |
| `--shadow-lg` | `0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)` | Floating modals, dialogs |
| `--shadow-xl` | `0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)` | Fullscreen sheets, navigation drawers |

### 2.4 Breakpoint Scale
| Breakpoint | Minimum Width | Target Devices |
| :--- | :--- | :--- |
| `sm` | `640px` | Large smartphones (landscape), small tablets |
| `md` | `768px` | Tablets (portrait), foldables |
| `lg` | `1024px` | Small laptops, tablets (landscape) |
| `xl` | `1280px` | Desktop workstations |
| `2xl` | `1536px` | Ultra-wide displays |

---

## 3. Semantic Tokens Reference

Semantic tokens automatically shift values depending on the active theme mode (`[data-theme='light']` or `[data-theme='dark']`):

| Semantic Variable | Light Default | Dark Default | Functional Meaning |
| :--- | :--- | :--- | :--- |
| `--background` | `#ffffff` | `#09090b` | Base page canvas |
| `--foreground` | `#09090b` | `#fafafa` | Primary text and headings |
| `--card` | `#ffffff` | `#18181b` | Elevated container surface |
| `--card-foreground` | `#09090b` | `#fafafa` | Text inside card surfaces |
| `--primary` | `#ea580c` | `#ea580c` | Primary brand accent / CTAs |
| `--primary-foreground`| `#ffffff` | `#ffffff` | Text on primary brand backgrounds |
| `--secondary` | `#f4f4f5` | `#27272a` | Secondary action buttons |
| `--secondary-foreground`| `#18181b`| `#fafafa` | Text on secondary buttons |
| `--muted` | `#f4f4f5` | `#27272a` | Inactive backgrounds, skeleton base |
| `--muted-foreground` | `#71717a` | `#a1a1aa` | Subtitles, helper text, timestamps |
| `--accent` | `#f4f4f5` | `#27272a` | Hover states, tab active chips |
| `--accent-foreground` | `#18181b` | `#fafafa` | Text on accent surfaces |
| `--destructive` | `#dc2626` | `#ef4444` | Danger actions, errors |
| `--destructive-foreground`| `#ffffff` | `#ffffff` | Text on danger actions |
| `--border` | `#e4e4e7` | `#27272a` | Component borders, table dividers |
| `--input` | `#e4e4e7` | `#27272a` | Form control outline borders |
| `--ring` | `#ea580c` | `#ea580c` | Keyboard focus indicator |
