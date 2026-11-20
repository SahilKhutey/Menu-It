# 03 — Module Ownership & Responsibilities Matrix

**Specification:** ARC-04 §4.1, §5  
**Project:** ModularMenu  

---

## 1. 16-Module Inventory & Ownership

| Module ID | Module Name | Priority | Owned Aggregates | Non-Responsibilities | Provided Contracts | Consumed Contracts |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MOD-01** | Identity & Auth | P0 | User Account, Session | Restaurant permissions, billing | `IdentityVerifier` | None |
| **MOD-02** | Tenant & Organization | P0 | Organization, Invitation | Menu content, password storage | `OrganizationReader` | `IdentityVerifier` |
| **MOD-03** | Restaurant Management | P0 | Restaurant, Settings | Menu items, prices, themes | `RestaurantReader` | `OrganizationReader` |
| **MOD-04** | Menu Management | P0 | Menu | Publishing, pricing records | `MenuReader` | `RestaurantReader`, `CategoryReader` |
| **MOD-05** | Category Management | P0 | Category | Food item descriptions, prices | `CategoryReader` | `MenuReader` |
| **MOD-06** | Food Item Management | P0 | Food Item | Currency, prices, themes | `FoodItemReader` | `CategoryReader`, `MediaStorage` |
| **MOD-07** | Pricing & Availability | P0 | Item Commercial Config | Dish descriptions, images | `PricingReader` | `FoodItemReader` |
| **MOD-08** | Theme Engine | P0 | Theme Configuration | Menu editing, direct rendering | `ThemeResolver` | None |
| **MOD-09** | Layout Engine | P0 | Layout Definition | Component code execution | `LayoutResolver` | `ComponentRegistryReader` |
| **MOD-10** | Component Registry | P0 | Component Definition | Arbitrary executable uploads | `ComponentRegistryReader`| None |
| **MOD-11** | Menu Rendering Engine | P0 | None (Transform Service) | Writing to menu/draft tables | `MenuRenderer` | `ThemeResolver`, `LayoutResolver`, `ComponentRegistryReader`, `PublishedSnapshotReader` |
| **MOD-12** | Visual Menu Editor | P0 | Editor Draft | Direct mutation of published snapshots | `EditorDraftManager` | `ThemeResolver`, `LayoutResolver`, `ComponentRegistryReader`, `MenuReader` |
| **MOD-13** | Publishing & Versioning | P0 | Publication | Direct editing of catalog | `PublishedSnapshotReader` | `MenuReader`, `CategoryReader`, `FoodItemReader`, `PricingReader`, `ThemeResolver` |
| **MOD-14** | Media Management | P1 | Media Asset | Deciding item publishability | `MediaStorage` | None |
| **MOD-15** | Subscription & Licensing| P1 | Subscription, License | Core authentication, bypassing auth | `LicenseEvaluator` | `OrganizationReader` |
| **MOD-16** | Analytics & Integrations| P2 | Integration, UsageEvent | Core menu workflows | `AnalyticsRecorder` | None |
