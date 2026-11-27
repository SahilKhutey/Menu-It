# FCD-11 · Document 03: Data Classification & Protection Policy

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Data Classification Tiers

Menu-It enforces strict handling requirements based on four data classification levels:

| Classification | Description | Examples | Protection Requirements |
| :--- | :--- | :--- | :--- |
| **Tier 1: Restricted (Secrets & Auth)** | Credentials, keys, passwords, and cryptographic material | Password hashes, JWT secrets, session tokens, private keys | Never logged; never exposed in API responses; redacted via `redact_data`; encrypted in transit and at rest |
| **Tier 2: Confidential (PII & Tenant Data)** | Identifiable personal information, financial data, and private tenant business data | Customer email addresses, phone numbers, payment metadata, revenue analytics, staff records | Tenant-isolated via PostgreSQL RLS; masked in non-debug logging; access restricted to authorized roles |
| **Tier 3: Internal (Operational Metadata)** | Telemetry, logs, execution metrics, and system configuration | Prometheus counters, job execution runtimes, trace IDs, service health status | Scrubbed of Tier 1 and Tier 2 data; accessible to platform operators and internal monitoring systems |
| **Tier 4: Public (Catalog & Branding)** | Data intentionally published to external consumers | Restaurant public profiles, active menu items, pricing, opening hours, restaurant logos | Cached on CDN/Edge; publicly queryable without authentication |

---

## 2. Sanitization & Masking Policy

- **Payment Card Data (PAN):** Menu-It never stores raw credit card PANs or CVVs. In logs and diagnostics, any detected card pattern is masked to `XXXX-****-XXXX` using `mask_card_number`.
- **Authorization Tokens:** In headers and query parameters, Bearer tokens and API keys are automatically replaced with `[REDACTED]` prior to logging.
- **Tenant Context Stripping:** When transmitting Tier 4 public menu data, internal organization identifiers and audit metadata are stripped from the response payload.
