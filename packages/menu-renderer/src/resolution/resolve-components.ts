import type { RenderNode } from "@modularmenu/contracts";

export function groupComponentsBySlot(nodes: RenderNode[]): Record<string, RenderNode[]> {
  const slots: Record<string, RenderNode[]> = {};
  for (const node of nodes) {
    if (!slots[node.slot]) {
      slots[node.slot] = [];
    }
    slots[node.slot].push(node);
  }
  return slots;
}
