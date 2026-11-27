# FCD-08 §08 — Theme Engine Architecture

## 1. Architectural Mission

The Menu-It Theme Engine (`packages/theme-engine`) orchestrates:
1. **Platform Theme Switching:** Dynamic toggling between `light`, `dark`, and `system` preferences.
2. **Tenant/Restaurant Customization:** Dynamic application of custom color palettes and typography for individual restaurant brands without stylesheet reloading.
3. **Strict Validation & Contrast Assurance:** Enforcing WCAG 2.2 AA contrast rules before custom themes can be injected into the DOM.
4. **SSR & Hydration Safety:** Zero flash of unstyled content (FOUC) and zero hydration mismatch errors during Next.js server-to-client handoff.

---

## 2. Component Structure

```mermaid
graph TD
    TP[ThemeProvider] --> SC[System Preference Listener]
    TP --> LS[localStorage Persistence]
    TP --> DOM[DOM Attribute & CSS Variable Injector]
    DOM --> A1[data-theme='light' | 'dark']
    DOM --> A2[data-restaurant-theme='bistro-classic']
    DOM --> A3[style='--primary: #881337; ...']
    V[validateTheme] --> DOM
```

### 2.1 Theme Definition Schema
A theme is defined by the `ThemeDefinition` interface:
```typescript
export interface ThemeColors {
  background: string;
  foreground: string;
  surface: string;
  surfaceMuted: string;
  primary: string;
  primaryForeground: string;
  secondary: string;
  secondaryForeground: string;
  muted: string;
  mutedForeground: string;
  border: string;
  input: string;
  ring: string;
  accent: string;
  accentForeground: string;
  destructive: string;
  destructiveForeground: string;
  success: string;
  warning: string;
  info: string;
}

export interface ThemeDefinition {
  id: string;
  name: string;
  version: number;
  isRestaurantTheme: boolean;
  colors: ThemeColors;
  typography: {
    fontFamily: string;
    baseFontSize: string;
  };
  radii: {
    card: string;
    button: string;
    input: string;
  };
}
```

---

## 3. Presets & Custom Themes

The Theme Engine provides four out-of-the-box verified theme presets:
1. **`platformLight`:** Default clean SaaS palette for administration and public web.
2. **`platformDark`:** High-contrast zinc/slate dark mode for platform operations.
3. **`bistroClassic`:** Warm burgundy (`#881337`) and cream palette for fine dining restaurants.
4. **`modernMinimal`:** Monochrome, sharp-radius styling for urban cafes and minimalist bistros.

All presets are statically verified to satisfy WCAG 2.2 AA contrast rules.
