# 11 — Transaction Consistency & Idempotency Strategy

**Specification:** ARC-04 §11  
**Project:** ModularMenu  

---

## 1. Consistency Model

ModularMenu employs a dual consistency model appropriate for a modular monolith:

### 1.1 Synchronous Consistency (ACID)
- Operations that must succeed or fail as a single atomic unit execute within a single PostgreSQL database transaction.
- **Examples:**
  - Creating an organization and assigning initial owner membership.
  - Generating a published snapshot record, updating the active version pointer, and emitting `MenuPublished`.
  - Creating a menu item alongside its initial price record.

### 1.2 Eventual Consistency (BASE)
- Operations that produce non-critical side effects or external telemetry execute asynchronously via in-process events or transactional outbox.
- **Examples:**
  - Recording page views and QR scan analytics (`MOD-16`).
  - Cache invalidation and CDN edge purging.
  - Background thumbnail generation for uploaded media assets (`MOD-14`).

---

## 2. Idempotency Guarantees

All retryable operations must provide deterministic idempotency:
- **Publication Requests:** If an identical candidate snapshot is resubmitted, the existing version is returned.
- **Analytics Ingestion:** Deduplication via `AnalyticsTracker.processed_event_ids` ensures duplicate event dispatches produce zero duplicate effects (`ARC04-T044`).
- **Domain Event Consumers:** Every event listener maintains an idempotency filter keyed on `event.event_id` (`ARC04-T048`).
