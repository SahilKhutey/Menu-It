# Service Operations Guide
**ModularMenu Operational Documentation**

## 1. Managing Services with Docker Compose
```bash
# View active service status
docker compose ps

# View unified streaming logs
docker compose logs -f --tail=100

# View specific service logs
docker compose logs -f backend
docker compose logs -f worker

# Restart a specific service gracefully
docker compose restart backend

# Stop the entire stack
docker compose down
```

## 2. Container Health & Inspection
```bash
# Check container resource usage
docker stats --no-stream

# Inspect health check output
docker inspect --format='{{json .State.Health}}' menu-backend | jq .
```\n