# Cache Invalidation Runbook
**CDN Edge & Server-Side Cache Purging**

## Cache Architecture
Public menu delivery uses version-addressed internal cache keys:
```
public-menu:{restaurant_id}:{menu_id}:{publication_id}
```
When `MenuPublished` or `MenuRolledBack` events are processed, the edge cache tags for `/r/{slug}/{menuSlug}` are purged.
