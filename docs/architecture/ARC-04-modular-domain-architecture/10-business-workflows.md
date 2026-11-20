# 10 — Core Business Workflows & Sequences

**Specification:** ARC-04 §10.4, §10.5, §10.6  
**Project:** ModularMenu  

---

## 1. Restaurant Onboarding Workflow (`VAL-ARC04-01`)

```mermaid
sequenceDiagram
    actor Admin as Restaurant Operator
    participant M01 as MOD-01 Identity
    participant M02 as MOD-02 Organization
    participant M03 as MOD-03 Restaurant

    Admin->>M01: RegisterUser(email, password)
    M01-->>Admin: UserCreated (UserRegistered event)
    Admin->>M02: CreateOrganization(name, owner_id)
    M02-->>Admin: OrganizationCreated
    Admin->>M03: CreateRestaurant(org_id, name, slug)
    M03->>M02: Check is_user_member(org_id, user_id)
    M02-->>M03: Authorized
    M03-->>Admin: RestaurantCreated (active, default settings)
```

---

## 2. Menu Creation & Editing Workflow (`VAL-ARC04-02`)

1. **MOD-04:** Creates menu in `DRAFT` status.
2. **MOD-05:** Creates categories with deterministic `display_order`.
3. **MOD-06:** Creates food items with dietary labels and allergen alerts.
4. **MOD-07:** Configures fixed-precision `Money` prices.
5. **MOD-12:** Coordinates visual studio editor sessions, maintaining reversible draft history (`undo`/`redo`) without mutating published menus.

---

## 3. Publication & Rollback Pipeline (`VAL-ARC04-04`)

```mermaid
sequenceDiagram
    actor Owner as Restaurant Owner
    participant M13 as MOD-13 Publishing
    participant M04 as MOD-04 to MOD-10
    participant M11 as MOD-11 Renderer

    Owner->>M13: PublishMenu(menu_id)
    M13->>M04: Read catalog, pricing, theme, and layout
    M04-->>M13: Validated candidate data
    M13->>M13: Compile immutable JSON snapshot & compute SHA-256
    M13->>M13: Assign incrementing version_number & activate pointer
    M13-->>Owner: MenuPublished (Active Version vN)
    
    opt Rollback
        Owner->>M13: RollbackPublication(menu_id, target_version_id)
        M13->>M13: Reactivate prior version pointer (vN-1)
        M13-->>Owner: PublicationRolledBack
    end
```
