# 25. API Risk Register

## 1. Managed Risks (`ARC07-R01` through `ARC07-R18`)
All 18 identified API architectural risks (including BOLA/IDOR, tenant spoofing, unbounded pagination, stale state overwrites, and webhook replay attacks) are fully mitigated through server-derived tenant contexts, token buckets, and HMAC signing.
