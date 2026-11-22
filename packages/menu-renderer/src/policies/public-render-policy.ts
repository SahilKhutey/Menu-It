import type { MenuRenderInput } from "@modularmenu/contracts";

export function isPublicDeliveryPermitted(input: MenuRenderInput): boolean {
  if (input.metadata.render_mode !== "published") {
    return false;
  }
  if (!input.publication || !input.publication.version) {
    return false;
  }
  return true;
}
