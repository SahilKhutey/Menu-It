import type { RenderCategory, RenderMenuItem } from "@modularmenu/contracts";

export function filterVisibleItems(items: RenderMenuItem[]): RenderMenuItem[] {
  return (items || []).filter((item) => item.availability !== "unavailable");
}

export function isCategoryEmpty(category: RenderCategory): boolean {
  return !category.items || category.items.length === 0;
}
