import { describe, expect, it } from "vitest";
import { deepMerge } from "../src/resolve";

describe("Theme Engine Resolve", () => {
  it("deeply merges token overrides into base tokens without mutation", () => {
    const base = {
      colors: {
        primary: "#ff0000",
        secondary: "#00ff00",
      },
      spacing: {
        unit: 8,
      },
    };

    const override = {
      colors: {
        primary: "#0000ff",
      },
    };

    const merged = deepMerge(base, override);

    expect(merged.colors.primary).toBe("#0000ff");
    expect(merged.colors.secondary).toBe("#00ff00");
    expect(merged.spacing.unit).toBe(8);

    // Assert base is not mutated
    expect(base.colors.primary).toBe("#ff0000");
  });
});
