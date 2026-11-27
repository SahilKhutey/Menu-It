# FCD-13 · Document 21 — Deferred Capabilities Register

## 1. Overview
FCD-13 certifies the integration, stability, and operational readiness of the platform foundation (FCD-01 to FCD-12). It does not claim the completion of the full restaurant SaaS commercial product. This register documents all capabilities intentionally deferred to subsequent business phases.

---

## 2. Deferred Business Capabilities Register

| Area | Deferred Capability | Target Phase | Dependency & Description |
| :--- | :--- | :---: | :--- |
| **Organization & Restaurants** | Comprehensive branch hierarchies, business operating hours editor UI, staff invitations | FCD-14 | Builds on FCD-04/FCD-05 membership resolver and FCD-06 restaurant profiles. |
| **Menu Engineering** | Interactive drag-and-drop menu editor, multi-level modifiers, allergen badges, digital QR menus | FCD-15 / FCD-16 | Builds on FCD-06 domain models and FCD-08 shared design system. |
| **Ordering & Kitchen (KDS)** | Live order placement, POS sync, WebSocket order streams, Kitchen Display System screens | FCD-17 / FCD-18 | Builds on FCD-10 async events and FCD-04 tenant isolation. |
| **Billing & Payments** | Stripe/Razorpay integration, multi-currency customer invoices, subscription billing | FCD-19 | Builds on FCD-06 `Money` value object and FCD-07 idempotency middleware. |
| **Cloud Adapters** | AWS S3 file storage, SendGrid / AWS SES email adapters | Post-FCD-13 | Plugs cleanly into FCD-09 `FileStorage` and `NotificationService` ports. |

---

## 3. Foundational Handoff Guarantee
All deferred business modules will build upon the immutable platform foundations established and certified in FCD-13 without needing to re-implement authentication, multi-tenancy, database persistence, caching, error envelopes, or CI/CD automation.
