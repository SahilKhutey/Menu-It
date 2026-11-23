# 14 — Customer-Hosted Architecture
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Turnkey Appliance Design
The customer-hosted edition enables restaurants and hospitality groups to own their complete hardware and data footprint.

## 2. Key Operational Features
- Single-command automated installation: `infrastructure/scripts/install-customer-hosted.sh`.
- Local directory initialization: `/var/lib/modularmenu/{data,media,backups}` with hardened file permissions (`chmod 600` on credentials).
- Offline self-sufficiency: Zero external SaaS phone-home requirements.
- Zero-dependency local media storage with HMAC signed access tokens.
- Optional single-node Redis with automatic in-memory fallback.\n