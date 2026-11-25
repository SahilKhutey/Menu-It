# FCD-08 §12 — Application Shell Architecture

## 1. Application Shell Models

Menu-It implements two distinct application shells reflecting its dual customer-facing and administrative operational models:

### 1.1 Customer-Facing Shell (`apps/web`)
- **Root Layout:** `apps/web/src/app/layout.tsx`
- **Focus:** Discovery, digital restaurant menus, mobile responsiveness, fast static generation.
- **Header:** Sticky or fixed header featuring the Menu-It brand mark, navigation links, and customer authentication link.
- **Footer:** Mobile-friendly footer with copyright, language, and legal information.
- **Styling:** Consumes `@menu-it/design-tokens/index.css` with warm brand accents and fluid typography.

### 1.2 Platform Administration Shell (`apps/admin`)
- **Root Layout:** `apps/admin/src/app/layout.tsx`
- **Focus:** High information density, data tables, platform operations, organization lifecycle management.
- **Header:** Compact utility header displaying platform status, active environment badge (`DEVELOPMENT` / `PRODUCTION`), and administrator profile.
- **Main Area:** Centered container (`<Container size="md">` or `<Container size="xl">`) holding administrative status cards, metrics, and data tables.
- **Styling:** Neutral cool slate/zinc palette (`--card`, `--border`, `--muted`) designed for fatigue-free extended operational usage.

---

## 2. Root Provider Integration Pattern

Both applications wrap their body content in the unified `ThemeProvider`:

```tsx
// RootLayout in apps/web/src/app/layout.tsx & apps/admin/src/app/layout.tsx
import '@menu-it/design-tokens/index.css';
import './globals.css';
import { ThemeProvider } from '@menu-it/theme-engine';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider defaultMode="system">
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

The attribute `suppressHydrationWarning` on `<html>` prevents React warning logs when client-side theme initialization synchronizes `data-theme` and `style="color-scheme: ..."` with local storage or OS settings.
