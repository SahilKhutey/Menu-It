# Background Worker Operations Guide
**ModularMenu Operational Documentation**

## 1. Monitoring Worker Activity
The worker polls the `outbox_events` table for unpublished events.
```bash
# Check worker process status
docker compose logs -f --tail=50 worker
```

## 2. Dead-Letter Queue (DLQ) Management
Inspect events that failed retry thresholds:
```sql
SELECT id, event_type, retry_count, last_error FROM outbox_events WHERE status = 'dead_letter';
```

### Reprocessing DLQ Events
```sql
UPDATE outbox_events SET status = 'pending', retry_count = 0 WHERE status = 'dead_letter';
```\n