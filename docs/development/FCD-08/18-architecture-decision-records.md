# FCD-08 §18 — Architecture Decision Records (ADRs)

## ADR-023: Three-Package Separation of Frontend Foundations
- **Status:** Accepted
- **Context:** Design tokens, theme logic, and UI components could either be combined into a single monolithic package or split into decoupled layers.
- **Decision:** Split into `@menu-it/design-tokens` (CSS custom properties, zero-dependency token scales), `@menu-it/theme-engine` (React provider, contrast calculation, validation, mode toggling), and `@menu-it/ui` (accessible React components).
- **Consequences:** Maximizes reusability, allows non-React consumers (e.g. static landing pages or emails) to import only design tokens, and simplifies isolated unit testing.

---

## ADR-024: CSS Custom Properties Over Runtime CSS-in-JS
- **Status:** Accepted
- **Context:** Styling dynamic themes can be accomplished via CSS-in-JS (e.g. styled-components, Emotion) or CSS Custom Properties (CSS variables).
- **Decision:** Use standard CSS custom properties combined with scoped utility classes.
- **Consequences:** Zero JavaScript runtime styling overhead, instant theme switching via single DOM property updates, complete compatibility with Next.js App Router and React Server Components (RSC), and zero CSS injection hydration warnings.

---

## ADR-025: Strict Automated WCAG 2.2 AA Contrast Enforcement
- **Status:** Accepted
- **Context:** Allowing multi-tenant restaurant administrators to customize colors risks producing illegible interfaces that fail accessibility laws.
- **Decision:** Implement relative luminance calculations in `validateTheme()` and reject any theme whose normal text contrast ratio is below 4.5:1.
- **Consequences:** Prevents inaccessible themes from reaching production DOM trees, guaranteeing legal and ethical accessibility compliance across all restaurant menus.

---

## ADR-026: Next.js Monorepo `transpilePackages` Direct Source Resolution
- **Status:** Accepted
- **Context:** Consuming monorepo packages in Next.js requires either a pre-build step (`pnpm build` generating `.js`/`.d.ts`) or direct source transpilation.
- **Decision:** Configure `transpilePackages` in `next.config.mjs` and export raw TypeScript source files (`src/index.ts`) with `moduleResolution: "bundler"`.
- **Consequences:** Eliminates tedious package rebuild steps during active development, enables instant Hot Module Reloading (HMR) across packages, and produces optimized tree-shaken production bundles.
