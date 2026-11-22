# ARC-08 §10 — CSS Variable & Style Generation

## 1. Naming Convention
Resolved tokens are flattened into CSS custom properties under the `--mm-` namespace:
- `tokens.color.brand.primary` $\to$ `--mm-color-brand-primary`
- `tokens.color.surface.default` $\to$ `--mm-color-surface-default`
- `tokens.typography.fontFamily.body` $\to$ `--mm-typography-fontFamily-body`
- `tokens.spacing.md` $\to$ `--mm-spacing-md`
- `tokens.radius.medium` $\to$ `--mm-radius-medium`

## 2. Scoped Injection Container (`ThemeScope`)
To prevent token leakage across multi-tenant administrative views or embedded widgets, variables are applied to a scoped CSS container:
```tsx
<div className="mm-theme-scope" style={cssVariables}>
  {children}
</div>
```
Zero global CSS pollution; zero runtime CSS-in-JS overhead.
