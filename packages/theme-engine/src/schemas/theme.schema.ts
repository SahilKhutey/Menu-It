import { meetsContrastAA } from '../resolvers/contrast';
import type { ThemeDefinition } from '../types/theme';

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

const HEX_COLOR_REGEX = /^#[0-9A-Fa-f]{6}$/;
const VALID_FONT_SIZES = new Set(['14px', '15px', '16px', '17px', '18px']);
const VALID_CARD_RADII = new Set(['0.25rem', '0.5rem', '0.75rem', '1rem', '1.5rem']);
const VALID_BUTTON_RADII = new Set(['0.25rem', '0.5rem', '0.75rem', '1rem', '9999px']);
const VALID_INPUT_RADII = new Set(['0.25rem', '0.5rem', '0.75rem']);

/**
 * Validates a theme definition against structure, color hex syntax, and WCAG AA contrast.
 */
export function validateTheme(theme: unknown): ValidationResult {
  const errors: string[] = [];

  if (!theme || typeof theme !== 'object') {
    return { valid: false, errors: ['Theme must be a non-null object.'] };
  }

  const def = theme as Partial<ThemeDefinition>;

  if (!def.id || typeof def.id !== 'string' || def.id.trim().length === 0) {
    errors.push('Theme ID must be a non-empty string.');
  }

  if (!def.name || typeof def.name !== 'string' || def.name.trim().length === 0) {
    errors.push('Theme name must be a non-empty string.');
  }

  if (typeof def.version !== 'number' || def.version < 1) {
    errors.push('Theme version must be a positive integer.');
  }

  const colors = def.colors;
  if (!colors || typeof colors !== 'object') {
    errors.push('Theme colors object is required.');
  } else {
    const requiredColors: (keyof typeof colors)[] = [
      'background',
      'foreground',
      'surface',
      'surfaceMuted',
      'primary',
      'primaryForeground',
      'secondary',
      'secondaryForeground',
      'muted',
      'mutedForeground',
      'border',
      'input',
      'ring',
      'accent',
      'accentForeground',
      'destructive',
      'destructiveForeground',
      'success',
      'successForeground',
      'warning',
      'warningForeground',
      'info',
      'infoForeground',
    ];

    for (const key of requiredColors) {
      const val = colors[key];
      if (typeof val !== 'string' || !HEX_COLOR_REGEX.test(val)) {
        errors.push(`Color '${key}' must be a 6-digit hex string (got '${val}').`);
      }
    }

    // Contrast validations (WCAG 2.2 AA)
    if (colors.foreground && colors.background && HEX_COLOR_REGEX.test(colors.foreground) && HEX_COLOR_REGEX.test(colors.background)) {
      if (!meetsContrastAA(colors.foreground, colors.background)) {
        errors.push(`Contrast failure: foreground (${colors.foreground}) on background (${colors.background}) must meet at least 4.5:1.`);
      }
    }

    if (colors.primaryForeground && colors.primary && HEX_COLOR_REGEX.test(colors.primaryForeground) && HEX_COLOR_REGEX.test(colors.primary)) {
      if (!meetsContrastAA(colors.primaryForeground, colors.primary)) {
        errors.push(`Contrast failure: primaryForeground (${colors.primaryForeground}) on primary (${colors.primary}) must meet at least 4.5:1.`);
      }
    }

    if (colors.destructiveForeground && colors.destructive && HEX_COLOR_REGEX.test(colors.destructiveForeground) && HEX_COLOR_REGEX.test(colors.destructive)) {
      if (!meetsContrastAA(colors.destructiveForeground, colors.destructive)) {
        errors.push(`Contrast failure: destructiveForeground (${colors.destructiveForeground}) on destructive (${colors.destructive}) must meet at least 4.5:1.`);
      }
    }
  }

  const typography = def.typography;
  if (!typography || typeof typography !== 'object') {
    errors.push('Theme typography object is required.');
  } else {
    if (!typography.fontFamily || typeof typography.fontFamily !== 'string') {
      errors.push('fontFamily must be a non-empty string.');
    }
    if (!VALID_FONT_SIZES.has(typography.baseFontSize)) {
      errors.push(`baseFontSize must be one of: ${Array.from(VALID_FONT_SIZES).join(', ')}.`);
    }
  }

  const radii = def.radii;
  if (!radii || typeof radii !== 'object') {
    errors.push('Theme radii object is required.');
  } else {
    if (!VALID_CARD_RADII.has(radii.card)) {
      errors.push(`radii.card must be one of: ${Array.from(VALID_CARD_RADII).join(', ')}.`);
    }
    if (!VALID_BUTTON_RADII.has(radii.button)) {
      errors.push(`radii.button must be one of: ${Array.from(VALID_BUTTON_RADII).join(', ')}.`);
    }
    if (!VALID_INPUT_RADII.has(radii.input)) {
      errors.push(`radii.input must be one of: ${Array.from(VALID_INPUT_RADII).join(', ')}.`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
