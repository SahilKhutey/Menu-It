# 31 — Cost & Operational Envelope
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Cloud Infrastructure Sizing & Cost Targets
- **SaaS Small Tier (1-50 restaurants):** 1x App Server (4 vCPU, 8 GB RAM), 1x Managed DB (2 vCPU, 4 GB RAM), S3 storage. Estimated monthly cost: $80 - $120.
- **SaaS Mid Tier (50-250 restaurants):** 2x App Servers (4 vCPU, 8 GB RAM), 1x Managed DB (4 vCPU, 16 GB RAM), S3 + Redis. Estimated monthly cost: $250 - $400.
- **Customer-Hosted Turnkey Appliance:** Single entry-level VPS or on-premise mini-PC (2 vCPU, 4 GB RAM, 50 GB SSD). Software licensing only; zero external cloud hosting fees.\n