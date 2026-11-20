# 03 — Entity Catalogue

## 1. Entity Groups and Ownership

| Group | Entities | Authoritative Owner |
|---|---|---|
| Identity | `users`, `user_sessions`, `password_reset_tokens` | Global Platform |
| Tenancy | `organizations`, `organization_members`, `organization_invitations` | Tenant (`organization_id`) |
| Restaurant | `restaurants`, `restaurant_members`, `restaurant_settings`, `restaurant_domains` | Branch (`organization_id`, `restaurant_id`) |
| Menu | `menus`, `menu_categories`, `menu_items` | Branch (`organization_id`, `restaurant_id`) |
| Pricing | `item_prices`, `item_variants`, `addons`, `item_addons`, `menu_item_translations` | Branch (`organization_id`, `restaurant_id`) |
| Presentation | `themes`, `restaurant_design_configs`, `layout_presets`, `component_definitions` | Platform Presets / Tenant Themes |
| Publishing | `menu_versions`, `publications` | Branch (`organization_id`, `restaurant_id`) |
| Media | `media_assets`, `media_usages` | Tenant (`organization_id`) |
| Licensing | `subscription_plans`, `subscriptions`, `licenses` | Platform / Tenant |
| Governance | `audit_logs`, `outbox_events`, `idempotency_records` | Tenant / Application |
