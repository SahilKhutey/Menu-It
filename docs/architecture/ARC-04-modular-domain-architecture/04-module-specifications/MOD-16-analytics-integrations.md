# MOD-16 — Analytics & Integrations Module Specification

**Module ID:** MOD-16  
**Tier:** Operational Capabilities (P2)  
**Package:** `app.modules.analytics`  

---

## 1. Ownership & Boundaries
- **Owns:** Usage events, event recording, analytics deduplication.
- **Does Not Own:** Menu catalog data, authentication tokens.

## 2. Domain Model & Invariants
- **UsageEvent Entity:** `UsageEvent(event_id, restaurant_id, event_type, metadata, recorded_at)`
- **AnalyticsTracker:** Enforces event idempotency through deduplication (`processed_event_ids`).

## 3. Public Contracts & Events
- **Provides:** `AnalyticsRecorder` Protocol (`record_page_view`).
- **Consumes:** None.
- **Emits:** `UsageEventRecorded` (EVT-018).
