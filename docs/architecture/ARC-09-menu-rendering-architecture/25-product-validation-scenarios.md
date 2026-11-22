# ARC-09 §25 — Product Validation Scenarios

## 1. 8 Product Validation Scenarios

1. **VAL-01: QR Code Guest Dining Journey**: Dining customer scans a table QR code on their smartphone, receives the published menu in <200ms with smooth horizontal category scrolling and instant price visibility.
2. **VAL-02: Peak Hour Concurrency**: Under sudden rush hour load (hundreds of guests opening menus simultaneously), Cloudflare Edge and local ETags serve 90%+ requests via HTTP 304 without touching the database.
3. **VAL-03: Real-Time Draft Previewing**: Restaurant manager alters dish prices and tests a new theme in the dashboard; preview page updates instantly with a warning banner without exposing unapproved edits to dining guests.
4. **VAL-04: Multi-Dietary Filtering**: Vegan, vegetarian, and gluten-sensitive guests filter dishes with clear, unmistakable visual indicators.
5. **VAL-05: Real-Time Out-of-Stock Handling**: When a dish runs out during dinner service, setting `is_available: false` visually greys out the item with an out-of-stock badge and disables action buttons.
6. **VAL-06: High-End Fine Dining Brand Expression**: Fine dining restaurant applies bespoke serif typography, gold-accented tokens, and full-bleed hero banners matching their brand standards.
7. **VAL-07: Offline & Poor Cellular Conditions**: On 3G connections, the lightweight HTML/CSS structure displays instantly while images load progressively in the background.
8. **VAL-08: Historical Snapshot Rollback**: When a seasonal menu ends, rolling back to the previous snapshot version instantly restores the prior menu and triggers automatic cache invalidation.
