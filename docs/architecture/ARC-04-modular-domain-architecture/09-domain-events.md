# 09 — Domain Events Catalogue & Contracts

**Specification:** ARC-04 §10  
**Project:** ModularMenu  

---

## 1. Domain Event Catalogue (EVT-001 to EVT-018)

| Event ID | Event Class | Owning Module | Business Trigger |
| :--- | :--- | :--- | :--- |
| **EVT-001** | `UserRegistered` | MOD-01 Identity | New user account created |
| **EVT-002** | `OrganizationCreated` | MOD-02 Organization | Organization established with owner |
| **EVT-003** | `MemberInvited` | MOD-02 Organization | Organization invitation issued |
| **EVT-004** | `RestaurantCreated` | MOD-03 Restaurant | Restaurant branch registered |
| **EVT-005** | `RestaurantDeactivated` | MOD-03 Restaurant | Restaurant marked inactive |
| **EVT-006** | `MenuCreated` | MOD-04 Menu | New menu initialized as draft |
| **EVT-007** | `CategoryCreated` | MOD-05 Category | Menu category created |
| **EVT-008** | `FoodItemCreated` | MOD-06 Food Item | Food dish record created |
| **EVT-009** | `ItemPriceChanged` | MOD-07 Pricing | Dish price updated |
| **EVT-010** | `ThemeUpdated` | MOD-08 Theme | Restaurant theme tokens modified |
| **EVT-011** | `LayoutConfigurationChanged`| MOD-09 Layout | Layout family or slot changed |
| **EVT-012** | `ComponentRegistered` | MOD-10 Component Registry| New approved component added |
| **EVT-013** | `DraftSaved` | MOD-12 Editor | Visual editor draft persisted |
| **EVT-014** | `MenuPublished` | MOD-13 Publishing | New immutable snapshot activated |
| **EVT-015** | `PublicationRolledBack` | MOD-13 Publishing | Prior published snapshot reactivated |
| **EVT-016** | `MediaUploaded` | MOD-14 Media | Image asset validated and stored |
| **EVT-017** | `EntitlementUpdated` | MOD-15 Licensing | Commercial entitlements modified |
| **EVT-018** | `UsageEventRecorded` | MOD-16 Analytics | Diner or operator telemetry logged |

---

## 2. Event Envelope & Invariant Rules
- Every event inherits from `DomainEvent` carrying `event_id: UUID`, `occurred_at: datetime`, `correlation_id: str | None`, and `schema_version: int`.
- Events represent immutable historical facts that have completed successfully; they are never commands.
- Event consumers must be idempotent (`ARC04-T048`).
- Events never contain sensitive passwords, session tokens, or private secrets.
