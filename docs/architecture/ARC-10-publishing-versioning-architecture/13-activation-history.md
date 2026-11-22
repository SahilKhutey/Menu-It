# ARC-10 §13: Activation History & Ledger
**Durable Traceability for Publication Movements**

## 1. Activation Ledger Schema
Every shift in the active publication pointer is recorded in `publication_activations`:
- `id`: Unique activation UUID.
- `menu_id`: Associated menu.
- `publication_id`: Newly activated publication ID.
- `previous_publication_id`: Replaced publication ID.
- `operation_id`: Correlating operation ID.
- `activation_reason`: `publish`, `rollback`, `scheduled`, or `recovery`.
- `actor_id`: User initiating the change.
- `activated_at`: UTC timestamp.
