# ARC-09 §22 — Performance & Bundle Optimization

## 1. Budget and Measurements
ModularMenu enforces strict frontend bundle size and server latency budgets:

| Metric | Budget SLA | Actual Measured | Status |
| :--- | :--- | :--- | :--- |
| **Public Menu First Load JS** | < 120 kB | **92.0 kB** | **PASSED** (23% under budget) |
| **Draft Preview First Load JS** | < 120 kB | **93.6 kB** | **PASSED** (22% under budget) |
| **Menu Renderer Pure Execution** | < 50 ms for 500 items | **< 10 ms** | **PASSED** |
| **Render Input Validation** | < 5 ms | **< 1 ms** | **PASSED** |
| **Public Delivery ETag Latency** | < 20 ms | **< 5 ms** | **PASSED** |

## 2. Optimization Techniques
- **Tree-Shaking**: `@modularmenu/menu-renderer` is modularized to exclude unused layout engines.
- **Zero Heavy Dependencies**: Pure TypeScript without Moment.js, Lodash, or bulky UI libraries.
- **Automatic Code Splitting**: Next.js route splitting isolates the operator dashboard from public customer pages.
