# ARC-08 §25 — Risk Register & Mitigations

| Risk ID | Description | Severity | Mitigation Strategy | Status |
| :--- | :--- | :--- | :--- | :--- |
| `RSK-01` | Arbitrary CSS / XSS Injection | High | Strict token whitelist; zero raw CSS injection; schema validation | Mitigated |
| `RSK-02` | Unbounded JSON Document Bloat | Med | 256 KB hard cap, max 100 components, max depth 10 enforced | Mitigated |
| `RSK-03` | Simultaneous Editor Overwrites | High | Optimistic concurrency control using `If-Match` revision tokens | Mitigated |
| `RSK-04` | Cross-Tenant Customization Leak| Critical | Multi-tenant join on `Restaurant.organization_id`; 404 on mismatch | Mitigated |
| `RSK-05` | Drift between Py & TS Resolvers| High | Shared JSON fixtures and identical deep-merge algorithms | Mitigated |
| `RSK-06` | Broken Menus from Schema Updates | High | Backward-compatible migrations; frozen published snapshots | Mitigated |
| `RSK-07` | Public Diner Latency Spike | Med | Zero runtime resolver calls in ARC-09; static CDN delivery | Mitigated |
| `RSK-08` | Contrast & Accessibility Failures | Med | Automated WCAG 2.1 AA token linting on base themes | Mitigated |
