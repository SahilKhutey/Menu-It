# 19. Rate Limiting and Resource Protection

## 1. Rate Limit Classes
Configured in `backend/architecture/api_rate_limits.yaml`:
- Public Diner Endpoints: 120 req/min per IP.
- Authenticated Tenant Endpoints: 600 req/min per user.
- Media Uploads: 30 req/min.
- Auth Mutations: 10 req/min (brute-force defense).
