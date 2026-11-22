import type { MenuRenderInput, RenderMenuItem, RenderCategory } from "@modularmenu/contracts";

export function normalizeMenuInput(input: MenuRenderInput): MenuRenderInput {
  if (!input || typeof input !== "object") {
    throw new Error("RENDER_INPUT_INVALID");
  }

  // Deep clone to avoid mutating source input
  const cloned: MenuRenderInput = JSON.parse(JSON.stringify(input));

  // Sort and filter categories
  if (Array.isArray(cloned.menu?.categories)) {
    const seenCatIds = new Set<string>();
    for (const cat of cloned.menu.categories) {
      if (seenCatIds.has(cat.id)) {
        throw new Error(`DUPLICATE_CATEGORY_ID: ${cat.id}`);
      }
      seenCatIds.add(cat.id);

      // Verify item uniqueness and sorting
      if (Array.isArray(cat.items)) {
        const seenItemIds = new Set<string>();
        for (const item of cat.items) {
          if (seenItemIds.has(item.id)) {
            throw new Error(`DUPLICATE_ITEM_ID: ${item.id}`);
          }
          seenItemIds.add(item.id);
        }
      }
    }
  }

  return cloned;
}
