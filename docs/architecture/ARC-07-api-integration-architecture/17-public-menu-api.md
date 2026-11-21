# 17. Public Menu API Architecture

## 1. Public Menu Endpoint
`GET /api/v1/public/{restaurant_slug}/{menu_slug}`
- Requires no authentication or tenant context.
- Reads directly from immutable `menu_publications` snapshot.
- Cached aggressively via Edge CDN with cache invalidation on new publication.
