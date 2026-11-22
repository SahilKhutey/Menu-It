# ARC-08 §18 — Public Menu Rendering Integration

## 1. Architectural Decoupling from ARC-09
When a menu is published (ARC-10):
1. The active customization draft is fully resolved into a static `published_snapshot`.
2. The snapshot contains resolved tokens, layout parameters, and visible component trees.
3. Public QR diners (ARC-09) fetch the immutable published release via CDN edge cache.
4. The public menu delivery pipeline performs **zero database lookups against `menu_customizations`** and executes **zero server-side resolution computations**.
5. Live restaurant drafts remain private to the dashboard and can be edited freely without impacting public diners.
