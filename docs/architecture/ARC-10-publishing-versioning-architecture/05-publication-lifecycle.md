# ARC-10 §5: Publication Lifecycle & State Machines
**Operational State Progression and Atomic Activation Flow**

## 1. Publication Operation State Machine
```
REQUESTED ──> VALIDATING ──> PREPARING ──> PREPARED ──> ACTIVATING ──> COMPLETED
     │              │             │                        │
     v              v             v                        v
  REJECTED       REJECTED       FAILED           RECONCILIATION_REQUIRED
```

## 2. Draft Lifecycle
```
ACTIVE_DRAFT ──(edit)──> DIRTY_DRAFT ──(save)──> SAVED_REVISION
                              │
                              v
                      READY_TO_PUBLISH ──(publish)──> PUBLISHED_SOURCE_REVISION
```

## 3. Publication Record Statuses
- **READY:** Snapshot is validated and ready for activation.
- **ACTIVE:** Snapshot is currently active and served publicly.
- **SUPERSEDED:** Snapshot was active, but a newer publication or rollback replaced it.
- **INACTIVE:** Valid historical snapshot not currently active.
- **REJECTED:** Validation failed; snapshot was never activated.
- **FAILED:** Execution failed during activation.
