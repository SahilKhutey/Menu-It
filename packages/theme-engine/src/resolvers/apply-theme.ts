import type { ThemeDefinition } from '../types/theme';
import { validateTheme } from '../schemas/theme.schema';

/**
 * Maps a ThemeDefinition to a dictionary of CSS custom property names and values.
 */
export function themeToCssVariables(theme: ThemeDefinition): Record<string, string> {
  return {
    '--background': theme.colors.background,
    '--foreground': theme.colors.foreground,
    '--surface': theme.colors.surface,
    '--surface-muted': theme.colors.surfaceMuted,
    '--primary': theme.colors.primary,
    '--primary-foreground': theme.colors.primaryForeground,
    '--secondary': theme.colors.secondary,
    '--secondary-foreground': theme.colors.secondaryForeground,
    '--muted': theme.colors.muted,
    '--muted-foreground': theme.colors.mutedForeground,
    '--border': theme.colors.border,
    '--input': theme.colors.input,
    '--ring': theme.colors.ring,
    '--accent': theme.colors.accent,
    '--accent-foreground': theme.colors.accentForeground,
    '--destructive': theme.colors.destructive,
    '--destructive-foreground': theme.colors.destructiveForeground,
    '--success': theme.colors.success,
    '--success-foreground': theme.colors.successForeground,
    '--warning': theme.colors.warning,
    '--warning-foreground': theme.colors.warningForeground,
    '--info': theme.colors.info,
    '--info-foreground': theme.colors.infoForeground,
    '--font-sans': theme.typography.fontFamily,
    '--radius-lg': theme.radii.card,
    '--radius-md': theme.radii.button,
    '--radius-sm': theme.radii.input,
  };
}

/**
 * Applies a verified ThemeDefinition to an HTML element (defaults to target or container).
 * Safely checks for DOM availability to avoid SSR crashes.
 */
export function applyTheme(theme: ThemeDefinition, targetElement?: HTMLElement): void {
  if (typeof window === 'undefined') {
    return;
  }

  const validation = validateTheme(theme);
  if (!validation.valid) {
    throw new Error(`Cannot apply invalid theme '${theme.id}': ${validation.errors.join('; ')}`);
  }

  const target = targetElement ?? document.documentElement;

  if (theme.isRestaurantTheme) {
    target.dataset.restaurantTheme = theme.id;
  } else {
    target.dataset.theme = theme.id;
  }

  const cssVars = themeToCssVariables(theme);
  for (const [prop, val] of Object.entries(cssVars)) {
    target.style.setProperty(prop, val);
  }
}

/**
 * Removes custom theme styles from an element.
 */
export function clearCustomTheme(targetElement?: HTMLElement): void {
  if (typeof window === 'undefined') {
    return;
  }
  const target = targetElement ?? document.documentElement;
  delete target.dataset.restaurantTheme;
}
