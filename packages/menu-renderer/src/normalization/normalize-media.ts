import type { RenderAsset } from "@modularmenu/contracts";

export function normalizeAssetUrl(
  asset?: RenderAsset | null,
  fallbackUrl: string = "/images/placeholder-dish.webp"
): { url: string; alt: string; width: number; height: number } {
  if (!asset || !asset.url) {
    return {
      url: fallbackUrl,
      alt: "Menu item presentation",
      width: 400,
      height: 300,
    };
  }

  // Reject javascript: or data: dangerous URLs
  const cleanUrl = asset.url.trim();
  if (cleanUrl.toLowerCase().startsWith("javascript:") || cleanUrl.toLowerCase().startsWith("data:text/html")) {
    return {
      url: fallbackUrl,
      alt: "Invalid media source",
      width: 400,
      height: 300,
    };
  }

  return {
    url: cleanUrl,
    alt: asset.alt || "Menu presentation",
    width: asset.width > 0 ? asset.width : 400,
    height: asset.height > 0 ? asset.height : 300,
  };
}
