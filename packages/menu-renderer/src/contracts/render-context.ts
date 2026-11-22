import type { RenderMode } from "@modularmenu/contracts";

export interface RenderContext {
  renderMode: RenderMode;
  locale: string;
  currency: string;
  minorUnitDigits: number;
  viewportPolicy: "mobile" | "tablet" | "desktop";
  assetBaseUrl?: string;
  timeEvaluatedAt: string;
}
