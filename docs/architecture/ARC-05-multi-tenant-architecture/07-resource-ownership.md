# 07 — Resource Ownership Architecture

## 1. 16-Module Ownership Matrix

| Module ID | Module Name | Resource | Primary Scope | RLS Enforced |
|---|---|---|---|---|
| MOD-01 | Identity | `users` | Global | No |
| MOD-02 | Organizations | `organizations`, `memberships` | `organization_id` | **Yes** |
| MOD-03 | Restaurants | `restaurants`, `restaurant_settings` | `organization_id`, `restaurant_id` | **Yes** |
| MOD-04 | Menus | `menus` | `organization_id`, `restaurant_id` | **Yes** |
| MOD-05 | Categories | `categories` | `organization_id`, `restaurant_id`, `menu_id` | **Yes** |
| MOD-06 | Food Items | `food_items` | `organization_id`, `restaurant_id` | **Yes** |
| MOD-07 | Pricing | `portion_prices`, `item_availabilities`| `organization_id`, `restaurant_id` | **Yes** |
| MOD-08 | Themes | `custom_themes` | `organization_id` | **Yes** |
| MOD-09 | Layouts | `layout_templates` | Global Presets | No |
| MOD-10 | Components | `component_definitions` | Global Presets | No |
| MOD-11 | QR Assets | `generated_qr_codes` | `organization_id`, `restaurant_id` | **Yes** |
| MOD-12 | Visual Studio | `editor_drafts` | `organization_id`, `restaurant_id` | **Yes** |
| MOD-13 | Publishing | `publications` | `organization_id`, `restaurant_id` | **Yes** |
| MOD-14 | Media | `media_assets` | `organization_id`, `restaurant_id` | **Yes** |
| MOD-15 | Analytics | `menu_views` | `organization_id`, `restaurant_id` | **Yes** |
| MOD-16 | Licensing | `subscriptions` | `organization_id` | **Yes** |
