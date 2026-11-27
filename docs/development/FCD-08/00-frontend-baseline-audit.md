# FCD-08 §00 — Frontend Baseline & Compatibility Audit

## 1. Executive Summary

Phase **FCD-08 — Frontend Foundation & Design System** establishes the visual, structural, and interactive foundation for the Menu-It frontend ecosystem.

Prior phases established the Next.js runtime skeletons (FCD-02), multi-tenant foundations (FCD-04), authentication integration (FCD-05), shared TypeScript contracts (FCD-06), and the frontend HTTP API client (FCD-07).

This audit documents the starting state of `apps/web` and `apps/admin` prior to FCD-08 design-system implementation to ensure that all existing application shells, layouts, and API integrations are preserved without regression.

---

## 2. Inventory of Existing Frontend Applications

### 2.1 Workspace Architecture
- **Package Manager:** `pnpm@11.11.0`
- **Root Workspace Filter:** `apps/*`, `packages/*`
- **Next.js Version:** `14.1.4` (resolving `14.2.35` engine)
- **React Version:** `18.2.0`
- **TypeScript:** `5.4.3` (`apps/web`, `apps/admin`), `5.8.2` (root, `packages/shared-types`)

### 2.2 Applications & Structure
| Application | Package Name | Port | Target Audience | Primary Routes |
| :--- | :--- | :--- | :--- | :--- |
| `apps/web` | `@menu-it/web` | 3000 | Diners, restaurant guests, restaurant managers | `/`, `manifest.ts`, `loading.tsx`, `error.tsx` |
| `apps/admin` | `@menu-it/admin` | 3001 | Platform operations & system administrators | `/`, `loading.tsx`, `error.tsx` |

### 2.3 Shared Packages (Current vs Required)
| Package | Location | Existing State | FCD-08 Target State |
| :--- | :--- | :--- | :--- |
| `@menu-it/shared-types` | `packages/shared-types` | Implemented (FCD-06 / FCD-07) | Retain & integrate with UI contracts |
| `@menu-it/design-tokens`| `packages/design-tokens` | Partial ts helper, no package.json | Full package: primitives, semantic, typography, spacing, breakpoints, index.css |
| `@menu-it/theme-engine` | `packages/theme-engine` | Partial resolver, no package.json | Full package: types, schemas, resolvers, providers, light/dark/system mode |
| `@menu-it/ui` | `packages/ui` | Not implemented | Full component library: Button, Input, Card, Container, Grid, Dialog, Tabs, Table |

---

## 3. Styling & Token Audit

### 3.1 Existing CSS Variables
- **`apps/web/src/app/globals.css`:**
  - `--background: #ffffff`, `--foreground: #181818`, `--surface: #f7f7f5`
  - `--border: #e8e8e5`, `--muted: #707070`, `--accent: #e46b3c`, `--radius: 14px`
  - Breakpoints: `--breakpoint-mobile: 640px`, `--breakpoint-tablet: 768px`, `--breakpoint-desktop: 1024px`, `--breakpoint-wide: 1440px`
- **`apps/admin/src/app/globals.css`:**
  - `--admin-background: #f5f6f8`, `--admin-surface: #ffffff`, `--admin-text: #191c24`
  - `--admin-muted: #707786`, `--admin-border: #e5e7ec`, `--admin-accent: #394b83`

### 3.2 Key Architectural Gaps Identified
1. **Ad-Hoc Variables:** Variables are duplicated in local `globals.css` rather than exported from a centralized design token package.
2. **Missing Dark Mode:** No dark mode or system theme detection is currently implemented.
3. **No Reusable Component Layer:** Buttons, inputs, and cards are styled via application-specific CSS classnames.
4. **Accessibility Deficits:** Focus rings (`:focus-visible`) are missing or unstandardized; color contrast ratios for dark theme are undefined.
5. **Restaurant Theme Isolation:** No runtime mechanism exists yet to scope custom restaurant branding strictly to public customer pages without polluting admin pages.

---

## 4. Audit Checklist Matrix

| Audit ID | Area | Target Specification | Status | Finding |
| :--- | :--- | :--- | :--- | :--- |
| **FE-AUD-01** | Next.js Version | Next.js App Router | PASS | `14.1.4` installed |
| **FE-AUD-02** | React Version | React 18 compatible | PASS | `18.2.0` installed |
| **FE-AUD-03** | TypeScript | Strict Mode | PASS | `strict: true` across all tsconfigs |
| **FE-AUD-04** | CSS Strategy | CSS Custom Properties + Modules/Scoped | PASS | Raw CSS variables in place, ready for design tokens |
| **FE-AUD-05** | Global Styles | Inventory variables | PASS | Documented in §3.1 |
| **FE-AUD-06** | UI Libraries | Check dependencies | PASS | Clean slate: zero heavy third-party UI dependencies |
| **FE-AUD-07** | Shared Packages | Monorepo pnpm mapping | EXTENSION | `pnpm-workspace.yaml` updated to include `packages/*` |
| **FE-AUD-08** | Routing | Next.js App Router | PASS | Verified in `apps/web` and `apps/admin` |
| **FE-AUD-09** | Providers | Root provider hierarchy | EXTENSION | ThemeProvider to be integrated at root layouts |
| **FE-AUD-10** | Fonts | System font stacks | PASS | Arial/Helvetica fallback; standardized via tokens |
| **FE-AUD-11** | API Client | FCD-07 API Client | PASS | `apiRequest<T>` intact in `apps/web` and `apps/admin` |
| **FE-AUD-12** | Responsive Shell | Mobile-first layout | PASS | Responsive viewport meta configured; tested down to 320px |
| **FE-AUD-13** | Tests | Component testing tools | EXTENSION | Unit & component tests to be added |
| **FE-AUD-14** | Production Build| Both apps build | IN PROGRESS | Verified via Next.js production build task |
