# ARC-09 §28 — Architecture Decision Records

## 1. Decision Records Summary (`ADR-0141` through `ADR-0167`)

- **ADR-0141**: Pure Presentation Engine Decoupled From Persistence.
- **ADR-0142**: Strict DTO Separation for Public Delivery vs Draft Preview.
- **ADR-0143**: Immutable Published Snapshots as Exclusive Source of Truth for Guests.
- **ADR-0144**: Deterministic SHA-256 Checksum Computation for ETags and Invalidation.
- **ADR-0145**: Standardized HTTP 304 Conditional GET Handling for High Concurrency.
- **ADR-0146**: Server-Side Rendering (SSR) via Next.js for SEO and Fast Initial Paint.
- **ADR-0147**: Mandatory Structural Slots (`header`, `navigation`, `category_section`, `item_card`, `footer`).
- **ADR-0148**: Controlled Component Registry with Explicit Error on Unknown Identifiers.
- **ADR-0149**: Safe Fallback Component Hierarchy for Missing or Deprecated Widgets.
- **ADR-0150**: CSS Design Tokens Scoped to `.theme-scope-container` Elements.
- **ADR-0151**: Prohibition of Raw Arbitrary User CSS Code Injection.
- **ADR-0152**: High-Visibility Visual Watermarking on Draft Previews.
- **ADR-0153**: Private No-Store Cache-Control Headers for Operator Previews.
- **ADR-0154**: Exact Decimal Arithmetic for Monetary Values and Non-Negativity Invariant.
- **ADR-0155**: Standard Currency Symbol Display Based on Restaurant Profile Currency.
- **ADR-0156**: Out-of-Stock Item Presentation Policy Support (Hide vs Disabled).
- **ADR-0157**: Standardized Dietary Badges and Spice Rating Normalization.
- **ADR-0158**: Responsive Breakpoint Architecture (Mobile 0-639px, Tablet 640-1023px, Desktop 1024px+).
- **ADR-0159**: Strict 120 kB First Load JavaScript Bundle Ceiling for Public Routes.
- **ADR-0160**: Fixed Aspect Ratio Containers to Prevent Cumulative Layout Shift (CLS).
- **ADR-0161**: Priority Image Preloading for Hero Covers and Lazy Loading Below Fold.
- **ADR-0162**: Mandatory Screen Reader Alt Text Generation on All Food Imagery.
- **ADR-0163**: WCAG 2.1 AA 4.5:1 Minimum Contrast Ratio Enforcement on Theme Presets.
- **ADR-0164**: Minimum 44x44px Touch Target Size for Interactive Elements.
- **ADR-0165**: Stateless Pure Function Execution for Concurrency Safety.
- **ADR-0166**: React Error Boundary Isolation for Resilient Partial Rendering.
- **ADR-0167**: Automated 120-Test Catalogue for Full Architecture Verification.
