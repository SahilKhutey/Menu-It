# FCD-04 — Operations & Incident Troubleshooting Runbook

## 1. Operational Procedures

### 1.1 Emergency Tenant Suspension
When an organization is flagged for security compromise, abuse, or critical payment default:
1. Update organization status to `SUSPENDED`:
   ```sql
   UPDATE organizations SET status = 'suspended', updated_at = clock_timestamp()
   WHERE id = '<ORGANIZATION_UUID>';
   ```
2. Insert an audit log entry:
   ```sql
   INSERT INTO organization_audit_events (organization_id, event_type, resource_type, resource_id, details)
   VALUES ('<ORGANIZATION_UUID>', 'organization.suspended', 'organization', '<ORGANIZATION_UUID>', '{"reason": "Security policy violation", "operator": "secops"}');
   ```
3. Immediate Effect:
   - Any further API request to that organization fails immediately with `HTTP 403 Forbidden` (`TenantSuspendedError`).

### 1.2 Reinstating a Suspended Organization
1. Validate account remediation.
2. Update organization status:
   ```sql
   UPDATE organizations SET status = 'active', updated_at = clock_timestamp()
   WHERE id = '<ORGANIZATION_UUID>' AND status = 'suspended';
   ```
3. Insert audit log record.

---

## 2. Troubleshooting & Diagnostic Guidance

### 2.1 Symptom: HTTP 404 on Known Organization
- **Cause**: User requesting the organization does not have an `active` membership in `organization_memberships`.
- **Diagnostic**:
  ```sql
  SELECT * FROM organization_memberships
  WHERE organization_id = '<ORG_UUID>' AND user_id = '<USER_UUID>';
  ```
- **Explanation**: Menu-It intentionally returns HTTP 404 rather than HTTP 403 when a user lacks membership, preventing attackers from probing valid organization UUIDs.

### 2.2 Symptom: RLS Policy Query Returns Empty Rows
- **Cause**: Query executed directly without transaction-local tenant context initialized.
- **Diagnostic**:
  ```sql
  SHOW app.current_organization_id;
  ```
  If empty, PostgreSQL RLS will filter out all rows where `organization_id` does not match null (i.e. all rows).
- **Resolution**: Ensure queries are executed through `tenant_transaction` or after calling `set_database_tenant_context(session, org_id)`.

### 2.3 Symptom: ContextVar Leaking Across Requests
- **Cause**: Coroutine yielded without resetting token in a `finally` block.
- **Verification**: Check that any custom service code uses the standard pattern:
  ```python
  token = set_current_tenant(ctx)
  try:
      # logic
  finally:
      reset_current_tenant(token)
  ```
