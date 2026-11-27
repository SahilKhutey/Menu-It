# FCD-12 · Document 11: Release Management & Versioning

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Semantic Versioning Specification

Menu-It follows SemVer 2.0.0: `MAJOR.MINOR.PATCH`
- **MAJOR:** Breaking API changes or relational schema incompatible rewrites.
- **MINOR:** Backward-compatible new business features (e.g. Menu publishing, KDS, Order processing).
- **PATCH:** Backward-compatible bug fixes, reliability patches, security updates.

---

## 2. Release Promotion Flow

```
 [ Feature Branch ] ──(PR + CI)──► [ develop Branch ]
                                         │
                                   Deploy to Staging
                                         │
                                   E2E & Smoke Verify
                                         │
                                   Manual Approval
                                         │
                                         ▼
                                   [ main Branch ]
                                         │
                                   Deploy to Production
                                         │
                                   Publish Git Tag (vX.Y.Z)
```
