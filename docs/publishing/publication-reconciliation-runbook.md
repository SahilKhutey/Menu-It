# Publication Reconciliation Runbook
**State Audit & Self-Healing Procedures**

## Runbook Steps
1. Execute `reconciliation_service.audit_menu_publications(menu_id)`.
2. Verify active publication pointer matches a valid record with status `ACTIVE`.
3. Verify SHA-256 hash matches the canonical snapshot payload.
4. If an in-flight transaction crashed, run `reconcile_active_pointer(menu_id)` to resolve the active state.
