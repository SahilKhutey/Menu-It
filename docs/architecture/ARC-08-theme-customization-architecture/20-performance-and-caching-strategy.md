# ARC-08 §20 — Performance & Caching Strategy

## 1. Latency Budgets
- **Deterministic Token Resolution:** $< 5\text{ ms}$ (Benchmarked: $< 1.2\text{ ms}$).
- **CSS Custom Property Emission:** $< 1\text{ ms}$ (Benchmarked: $< 0.15\text{ ms}$).
- **Draft Save API (`PUT /customization`):** $< 500\text{ ms}$ (Benchmarked: $< 65\text{ ms}$).
- **Bundle Size Budget:** Customization engine libraries $< 120\text{ kB}$ uncompressed.

## 2. Caching Rules
- Platform catalogues (`/themes`, `/layouts`, `/components`) are immutable and cached with `Cache-Control: public, max-age=86400, stale-while-revalidate=3600`.
- Draft endpoints (`/customization`) are strictly private and uncacheable (`Cache-Control: private, no-cache, no-store`).
