"""Standard cache policy definitions and TTL configurations (FCD-10 WP-02)."""

# Suggested standard TTLs in seconds
TTL_SHORT = 60          # 1 minute (frequently changing data)
TTL_MEDIUM = 300       # 5 minutes (standard menus, categories)
TTL_LONG = 600         # 10 minutes (restaurant public profile, static metadata)
TTL_VERY_LONG = 3600   # 1 hour (rarely changing tenant configuration)

DEFAULT_CACHE_TTL = TTL_MEDIUM
