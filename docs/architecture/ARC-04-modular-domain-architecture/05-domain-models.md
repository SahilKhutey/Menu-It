# 05 — Domain Models & Value Objects

**Specification:** ARC-04 §7  
**Project:** ModularMenu  

---

## 1. Domain Entities vs Value Objects

In ModularMenu, domain logic strictly separates entities (which have distinct lifecycles and unique identifiers) from value objects (which represent immutable validated concepts).

### Core Entities:
- **User** (`MOD-01`)
- **Organization** (`MOD-02`)
- **Restaurant** (`MOD-03`)
- **Menu** (`MOD-04`)
- **Category** (`MOD-05`)
- **FoodItem** (`MOD-06`)
- **Price** (`MOD-07`)
- **ThemeDefinition** (`MOD-08`)
- **LayoutDefinition** (`MOD-09`)
- **ComponentDefinition** (`MOD-10`)
- **EditorDraft** (`MOD-12`)
- **Publication** (`MOD-13`)
- **MediaAsset** (`MOD-14`)
- **License** (`MOD-15`)
- **UsageEvent** (`MOD-16`)

### Core Value Objects:
- **Money:** `Money(amount: Decimal, currency: str = "INR")` — non-negative finite Decimal, 3-letter currency code.
- **EmailAddress:** Normalized lowercase, max 254 chars, regex-validated.
- **RestaurantSlug & MenuSlug:** Lowercase, hyphen-delimited alphanumeric (`^[a-z0-9]+(?:-[a-z0-9]+)*$`).
- **DisplayOrder:** Non-negative integer (`>= 0`).
- **PublishedVersion:** Immutable snapshot record stamped with SHA-256 hash.
