# FCD-11 · Document 13: Sensitive Data Masking, Sanitization & Redaction

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Redaction Architecture

Menu-It implements recursive and pattern-based sanitization in `menu_it.platform.observability.redaction`:

- **Key-Based Redaction (`redact_data`):** Recursively traverses dictionaries and lists. Any key matching known sensitive terms (`password`, `secret`, `token`, `access_token`, `authorization`, `api_key`, `card_number`, `cvv`, etc.) has its value replaced with `"[REDACTED]"`.
- **Authorization Header Sanitization (`redact_authorization_header`):** Replaces bearer tokens or basic credentials with `Bearer [REDACTED]` or `Basic [REDACTED]`.
- **URL Query Parameter Sanitization (`redact_query_params`):** Parses URL query strings and replaces sensitive parameter values with `[REDACTED]`.
- **PAN Masking (`mask_card_number`):** Detects 13-to-19 digit credit card numbers and formats them as `XXXX-****-XXXX`, masking the sensitive central digits.

---

## 2. Invariant Guarantee

No plaintext password, raw bearer token, or unmasked credit card PAN shall ever appear in logs, traces, or metrics, regardless of logger level or exception state.
