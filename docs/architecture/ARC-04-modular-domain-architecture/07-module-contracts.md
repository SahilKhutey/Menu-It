# 07 — Module Contracts & Interfaces

**Specification:** ARC-04 §8  
**Project:** ModularMenu  

---

## 1. In-Process Protocol Contracts

ModularMenu enforces communication boundaries through Python `typing.Protocol` interfaces. Modules consume abstract protocols implemented by peer modules or application adapters, preventing direct ORM coupling.

### Key Public Protocols:
- `IdentityVerifier`: `verify_user_active(user_id: UUID) -> bool`
- `OrganizationReader`: `organization_exists(id: UUID) -> bool`, `is_user_member(org_id: UUID, user_id: UUID) -> bool`
- `RestaurantReader`: `restaurant_exists(id: UUID) -> bool`, `is_restaurant_active(id: UUID) -> bool`
- `MenuReader`: `menu_exists(menu_id: UUID, restaurant_id: UUID) -> bool`
- `CategoryReader`: `category_exists(category_id: UUID, menu_id: UUID) -> bool`
- `FoodItemReader`: `item_exists(item_id: UUID) -> bool`
- `PricingReader`: `get_item_price(item_id: UUID) -> Money | None`
- `ThemeResolver`: `resolve_theme(theme_id: str) -> dict[str, Any]`
- `LayoutResolver`: `get_layout(layout_id: str) -> LayoutDefinition | None`
- `ComponentRegistryReader`: `get_component(component_id: str, version: int = 1) -> ComponentDefinition | None`
- `MenuRenderer`: `render(data: RenderInput) -> RenderResult`
- `EditorDraftManager`: `get_draft_configuration(restaurant_id: UUID) -> dict[str, Any] | None`
- `PublishedSnapshotReader`: `get_active_snapshot(menu_id: UUID) -> dict[str, Any] | None`
- `MediaStorage`: `resolve_media_url(asset_id: UUID) -> str | None`
- `LicenseEvaluator`: `is_feature_entitled(organization_id: UUID, feature_key: str) -> bool`
- `AnalyticsRecorder`: `record_page_view(restaurant_id: UUID) -> None`
