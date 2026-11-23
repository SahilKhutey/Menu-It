# Runbook: Worker Backlog & Outbox Congestion
**ModularMenu Emergency Runbook**

## 1. Symptoms
- Menu publication updates take minutes to propagate.
- High count of `pending` records in `outbox_events`.

## 2. Diagnostic Steps
```bash
# Query pending event count
docker compose exec postgres psql -U menu_user -d modularmenu -c "SELECT count(*) FROM outbox_events WHERE status = 'pending';"

# Inspect worker logs
docker compose logs --tail=100 worker
```

## 3. Remediation
- Restart hung worker process: `docker compose restart worker`.
- If DLQ has poison pills, inspect error messages and mark processed.\n