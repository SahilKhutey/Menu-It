/**
 * ModularMenu — Design Tokens to CSS Variables Generator (ARC-08 §5.3, §16.3).
 * Strictly converts validated tokens to allowed CSS custom property declarations.
 */

export function toCssVariables(tokens: Record<string, any>): Record<string, string> {
  const vars: Record<string, string> = {};

  if (!tokens || typeof tokens !== "object") {
    return vars;
  }

  // Colors
  const color = tokens.color || {};
  if (color.brand) {
    if (color.brand.primary) vars["--mm-color-brand-primary"] = color.brand.primary;
    if (color.brand.secondary) vars["--mm-color-brand-secondary"] = color.brand.secondary;
    if (color.brand.accent) vars["--mm-color-brand-accent"] = color.brand.accent;
  }
  if (color.surface) {
    if (color.surface.default) vars["--mm-color-surface-default"] = color.surface.default;
    if (color.surface.subtle) vars["--mm-color-surface-subtle"] = color.surface.subtle;
    if (color.surface.raised) vars["--mm-color-surface-raised"] = color.surface.raised;
  }
  if (color.text) {
    if (color.text.primary) vars["--mm-color-text-primary"] = color.text.primary;
    if (color.text.secondary) vars["--mm-color-text-secondary"] = color.text.secondary;
    if (color.text.inverse) vars["--mm-color-text-inverse"] = color.text.inverse;
  }
  if (color.border) {
    if (color.border.default) vars["--mm-color-border-default"] = color.border.default;
    if (color.border.subtle) vars["--mm-color-border-subtle"] = color.border.subtle;
  }
  if (color.status) {
    if (color.status.success) vars["--mm-color-status-success"] = color.status.success;
    if (color.status.warning) vars["--mm-color-status-warning"] = color.status.warning;
    if (color.status.error) vars["--mm-color-status-error"] = color.status.error;
  }

  // Typography
  const typography = tokens.typography || {};
  if (typography.fontFamily) {
    if (typography.fontFamily.body) vars["--mm-font-family-body"] = typography.fontFamily.body;
    if (typography.fontFamily.heading) vars["--mm-font-family-heading"] = typography.fontFamily.heading;
  }
  if (typography.fontSize) {
    if (typography.fontSize.small) vars["--mm-font-size-small"] = typography.fontSize.small;
    if (typography.fontSize.body) vars["--mm-font-size-body"] = typography.fontSize.body;
    if (typography.fontSize.heading) vars["--mm-font-size-heading"] = typography.fontSize.heading;
    if (typography.fontSize.display) vars["--mm-font-size-display"] = typography.fontSize.display;
  }
  if (typography.fontWeight) {
    if (typography.fontWeight.normal) vars["--mm-font-weight-normal"] = String(typography.fontWeight.normal);
    if (typography.fontWeight.medium) vars["--mm-font-weight-medium"] = String(typography.fontWeight.medium);
    if (typography.fontWeight.bold) vars["--mm-font-weight-bold"] = String(typography.fontWeight.bold);
  }

  // Spacing
  const spacing = tokens.spacing || {};
  for (const [key, val] of Object.entries(spacing)) {
    if (typeof val === "string") {
      vars[`--mm-spacing-${key}`] = val;
    }
  }

  // Radius
  const radius = tokens.radius || {};
  for (const [key, val] of Object.entries(radius)) {
    if (typeof val === "string") {
      vars[`--mm-radius-${key}`] = val;
    }
  }

  // Shadow
  const shadow = tokens.shadow || {};
  for (const [key, val] of Object.entries(shadow)) {
    if (typeof val === "string") {
      vars[`--mm-shadow-${key}`] = val;
    }
  }

  return vars;
}
