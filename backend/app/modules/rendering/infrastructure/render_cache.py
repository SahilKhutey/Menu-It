"""
Render Cache Infrastructure and HTTP Header Policies (ARC-09 §9, WP-ARC09-08).
"""
import hashlib
from typing import Dict
from app.modules.rendering.domain.render_mode import RenderMode


class RenderCachePolicy:
    """Manages cache keys, ETags, and Cache-Control headers for menu delivery."""

    @staticmethod
    def generate_cache_key(restaurant_slug: str, menu_slug: str, checksum: str) -> str:
        """Computes deterministic cache key for CDN or memory stores."""
        raw = f"modularmenu:render:{restaurant_slug}:{menu_slug}:{checksum}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_etag(checksum: str) -> str:
        """Generates standard HTTP ETag header value."""
        clean = checksum.strip('"')
        return f'"{clean}"'

    @staticmethod
    def get_cache_headers(mode: RenderMode, checksum: str) -> Dict[str, str]:
        """Returns standard HTTP caching headers based on render mode."""
        if mode == RenderMode.PUBLIC_PUBLISHED:
            return {
                "Cache-Control": "public, max-age=60, s-maxage=300, stale-while-revalidate=86400",
                "ETag": RenderCachePolicy.generate_etag(checksum),
                "Vary": "Accept-Encoding",
            }
        elif mode == RenderMode.DRAFT_PREVIEW:
            return {
                "Cache-Control": "private, no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        else:
            return {
                "Cache-Control": "no-store",
            }
