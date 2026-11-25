# FCD-08 §05 — Typography System

## 1. Font Family Architecture

Menu-It defines a robust multi-tiered font stack optimized for cross-platform rendering, legibility, and brand flexibility:

```css
/* Primary Sans-Serif Font Stack */
--font-family-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";

/* Monospace Font Stack (Identifiers, Timestamps, Code, API payloads) */
--font-family-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;

/* Heading Font Stack */
--font-family-heading: var(--font-family-sans);
```

---

## 2. Type Scale & Hierarchy

The typographic scale uses harmonic geometric steps balanced for readability on both desktop workstations and handheld devices:

| Step | CSS Variable | Rem Value | Pixel Value | Line Height | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Micro** | `--font-size-xs` | `0.75rem` | `12px` | `1rem` (16px) | Badges, metadata tags, breadcrumb hints |
| **Small** | `--font-size-sm` | `0.875rem` | `14px` | `1.25rem` (20px) | Form input labels, helper text, table data |
| **Base** | `--font-size-base` | `1rem` | `16px` | `1.5rem` (24px) | Default body copy, button labels |
| **Large** | `--font-size-lg` | `1.125rem` | `18px` | `1.75rem` (28px) | Card titles, modal headers, lead summaries |
| **XL** | `--font-size-xl` | `1.25rem` | `20px` | `1.75rem` (28px) | Section headers, table caption headers |
| **2XL** | `--font-size-2xl` | `1.5rem` | `24px` | `2rem` (32px) | Subheadings, page subtitle titles |
| **3XL** | `--font-size-3xl` | `1.875rem` | `30px` | `2.25rem` (36px) | Page primary titles (`h1`) |
| **4XL** | `--font-size-4xl` | `2.25rem` | `36px` | `2.5rem` (40px) | Admin console top headers |
| **Hero** | `--font-size-hero` | `clamp(2.5rem, 6vw, 4.5rem)` | `40px–72px` | `1.05` | Landing page marketing hero titles |

---

## 3. Font Weights & Letter Spacing

| Weight Role | Token | Value | Applied To |
| :--- | :--- | :--- | :--- |
| **Normal** | `--font-weight-normal` | `400` | Standard body copy, descriptions |
| **Medium** | `--font-weight-medium` | `500` | Form labels, navigation links, table headers |
| **Semibold** | `--font-weight-semibold` | `600` | Button text, card titles, section headings |
| **Bold** | `--font-weight-bold` | `700` | Eyebrow badges, metric numbers |
| **Extrabold** | `--font-weight-extrabold` | `800` | Brand logo mark (`Menu-It`), hero display |

Letter spacings (`letter-spacing`) are calibrated to maximize clarity:
- **Tight:** `-0.025em` for large display headings to maintain cohesion.
- **Normal:** `0em` for body copy.
- **Wide:** `0.05em` to `0.1em` for uppercase eyebrow badges and status tags.
