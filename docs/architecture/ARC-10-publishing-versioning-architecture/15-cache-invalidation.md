# ARC-10 §15: Cache Invalidation & Delivery
**Version-Aware Caching & Instantaneous Purge**

## 1. Version-Addressed Cache Keys
Internal cache keys incorporate publication identity:
```
public-menu:{restaurant_id}:{menu_id}:{publication_id}
```
The stable URL `/r/{restaurant_slug}/{menu_slug}` resolves the active publication ID.

## 2. Invalidation Flow
Upon receiving `MenuPublished` or `MenuRolledBack` events:
1. Invalidate edge CDN cache tags for the menu.
2. Invalidate internal application server-side render caches.
3. Emit fresh ETag stamped with snapshot SHA-256 digest.
