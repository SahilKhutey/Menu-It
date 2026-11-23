# Runbook: Tenant Data Incident / Suspected Leakage
**ModularMenu Emergency Runbook**

## 1. Immediate Containment
1. If data leakage suspected, immediately throttle public API access.
2. Confirm Row-Level Security (RLS) is active on all tenant tables:
```sql
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
```
3. Audit recent queries in PostgreSQL logs for missing `app.current_org_id` context.
4. Notify Data Protection Officer and begin formal breach triage protocol.\n