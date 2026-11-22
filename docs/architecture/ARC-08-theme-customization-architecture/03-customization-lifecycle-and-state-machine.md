# ARC-08 §3 — Customization Lifecycle & State Machine

```mermaid
stateDiagram-v2
    [*] --> DefaultDraft: Menu Created
    DefaultDraft --> ValidatedDraft: Edit (Settings or Visual)
    ValidatedDraft --> EphemeralPreview: Request Preview (POST /preview)
    ValidatedDraft --> SavedDraft: Save with If-Match (PUT /customization)
    SavedDraft --> RevisionCreated: Increment Revision + Persist
    RevisionCreated --> SavedDraft: Continue Editing
    RevisionCreated --> RestoredDraft: Restore Revision (POST /restore)
    RevisionCreated --> PublishedSnapshot: Publish Menu (ARC-10)
    PublishedSnapshot --> PublicDelivery: Served via CDN (ARC-09)
```

### Lifecycle States
- **Draft:** Working customization state stored in `menu_customizations`. Mutable only through optimistic concurrency updates.
- **Revision History:** Immutable historical revisions stored in `customization_revisions`.
- **Ephemeral Preview:** In-memory resolved tokens and component tree generated without persisting to disk.
- **Published Snapshot:** Frozen, immutable customization snapshot embedded in the published menu release (ARC-10), completely decoupled from future draft changes.
