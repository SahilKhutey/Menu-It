# 02 — Bounded Contexts & Ubiquitous Language

**Specification:** ARC-04 §5  
**Project:** ModularMenu  

---

## 1. Context Boundaries Overview

A bounded context encapsulates a specific ubiquitous language, domain models, and business invariants:

| Context Name | Owning Modules | Ubiquitous Vocabulary | Invariant Boundary |
| :--- | :--- | :--- | :--- |
| **Identity Context** | MOD-01 | User, Credential, Session, Token | Secure credentials, password hashing, session lifecycle. |
| **Organization Context** | MOD-02 | Organization, Member, Role, Invitation | Commercial ownership, membership access rules. |
| **Restaurant Context** | MOD-03 | Restaurant, Profile, Slug, Settings | Business identity, locale, timezones, brand metadata. |
| **Menu Catalog Context** | MOD-04, 05, 06, 07 | Menu, Category, FoodItem, Price, Addon | Menus, categories, food items, and money pricing. |
| **Experience Context** | MOD-08, 09, 10, 12 | Theme, Token, Layout, Component, Draft | Declarative design tokens, layouts, safe component registry. |
| **Delivery Context** | MOD-11, 13 | Publication, Snapshot, RenderResult | Immutable published snapshots, SHA-256 digests, rollbacks. |
| **Commercial Context** | MOD-14, 15, 16 | MediaAsset, License, Entitlement, Event | Asset storage, licensing entitlements, usage tracking. |

---

## 2. Invariant Isolation Rules
- **Content vs Presentation:** Modifying a menu dish description does not alter the theme; editing theme tokens does not alter menu catalog data.
- **Drafts vs Published Versions:** Changes made in the Visual Editor operate on drafts (`MOD-12`) and never mutate the active published snapshot (`MOD-13`).
- **Identity vs Licensing:** Authenticating a user (`MOD-01`) does not require a paid license (`MOD-15`). Licensing governs feature entitlements, not security credentials.
