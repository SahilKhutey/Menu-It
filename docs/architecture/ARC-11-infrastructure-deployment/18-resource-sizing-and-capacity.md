# 18 — Resource Sizing & Capacity Planning
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Resource Allocations by Deployment Profile
| Component | Local Dev | Customer-Hosted (Min) | Customer-Hosted (Rec) | SaaS Production (Per Node) |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | 0.5 CPU / 512 MB | 0.5 CPU / 512 MB | 1.0 CPU / 1 GB | 2.0 CPU / 2 GB |
| **Backend API** | 0.5 CPU / 512 MB | 0.5 CPU / 512 MB | 1.0 CPU / 1 GB | 2.0 CPU / 4 GB |
| **Worker** | 0.25 CPU / 256 MB| 0.25 CPU / 256 MB| 0.5 CPU / 512 MB | 1.0 CPU / 1 GB |
| **PostgreSQL**| 0.5 CPU / 512 MB | 0.5 CPU / 1 GB | 1.0 CPU / 2 GB | 4.0 CPU / 8 GB |
| **Redis** | 0.25 CPU / 128 MB| Optional (128 MB)| 0.25 CPU / 256 MB| 1.0 CPU / 1 GB |
| **Disk Space**| 10 GB | 20 GB | 50 GB SSD | 200 GB NVMe |\n