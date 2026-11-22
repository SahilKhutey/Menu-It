# ARC-09 §27 — Risk Register & Mitigations

## 1. Technical Risk Assessment

| Risk ID | Risk Description | Severity | Probability | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | Database overload during peak QR scanning | High | Medium | CDN edge caching with 5-minute s-maxage and ETag conditional GETs |
| **RSK-02** | Accidental leak of unpublished dishes or prices | Critical | Low | Strict separate DTO models for public vs draft endpoints; immutable snapshots |
| **RSK-03** | Frontend bundle size exceeding 120 kB ceiling | Medium | Medium | Decoupled renderer package, zero heavy date/math libraries, strict code splitting |
| **RSK-04** | Cumulative Layout Shift (CLS) from slow image loads | Medium | High | Fixed aspect ratio containers (16:9, 1:1) and Next.js image priority flags |
| **RSK-05** | Malicious CSS injection via custom theme tokens | High | Low | Regex validation requiring strict `#RRGGBB` hex color format |
| **RSK-06** | Browser crash from corrupted third-party layout | Medium | Low | React error boundary wrapping each section to isolate failures gracefully |
