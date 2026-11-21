# 20. API Security Requirements

## 1. Security Baseline
- TLS 1.3 encryption required for all external communication.
- CORS restricted to configured tenant domains (`PUBLIC_BASE_URL`).
- Request body limits (max 10 MB for uploads, max 1 MB for JSON).
- Security headers: HSTS, Content-Security-Policy, X-Frame-Options: DENY.
