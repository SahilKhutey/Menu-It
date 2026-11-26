# FCD-11 · Document 08: API Security, Input Validation & Browser Protection

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Browser Security Headers

The `SecurityHeadersMiddleware` automatically injects hardened response headers on all HTTP endpoints:

| Header | Value | Purpose |
| :--- | :--- | :--- |
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-sniffing attacks |
| `X-Frame-Options` | `DENY` | Prevents clickjacking by forbidding embedding in frames |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Protects private URL parameters on external navigation |
| `Permissions-Policy` | `geolocation=(), camera=(), microphone=(), payment=()` | Disables sensitive browser device hardware APIs |
| `Cross-Origin-Opener-Policy` | `same-origin` | Isolates browsing context against Spectre/XS-Leaks |
| `Cross-Origin-Resource-Policy`| `same-site` | Protects backend resources against cross-origin reads |
| `Content-Security-Policy` | `default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'` | Restricts script sources and frames |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Enforces HTTPS on secure connections |

---

## 2. Input Validation & Schema Strictness

- All request bodies are strictly typed via Pydantic v2 schemas.
- Extra unknown fields are handled predictably.
- IDs, UUIDs, phone numbers, and emails are validated via regex/parsers before touching service layers.
