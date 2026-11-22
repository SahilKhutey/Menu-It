import type { RenderMenuItem, RenderAsset } from "@modularmenu/contracts";

export function getPrimaryItemImage(item: RenderMenuItem): RenderAsset | undefined {
  if (!item.images || item.images.length === 0) return undefined;
  return item.images.find((img) => img.is_primary) || item.images[0];
}
