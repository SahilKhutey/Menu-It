/**
 * WCAG 2.2 Relative Luminance and Contrast Ratio Calculator.
 */

function hexToRgb(hex: string): [number, number, number] {
  const sanitized = hex.replace('#', '').trim();
  const bigint = parseInt(sanitized, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return [r, g, b];
}

function channelLuminance(channel: number): number {
  const norm = channel / 255;
  return norm <= 0.03928 ? norm / 12.92 : Math.pow((norm + 0.055) / 1.055, 2.4);
}

export function getRelativeLuminance(hexColor: string): number {
  const [r, g, b] = hexToRgb(hexColor);
  return 0.2126 * channelLuminance(r) + 0.7152 * channelLuminance(g) + 0.0722 * channelLuminance(b);
}

export function getContrastRatio(hexA: string, hexB: string): number {
  const lumA = getRelativeLuminance(hexA);
  const lumB = getRelativeLuminance(hexB);
  const lighter = Math.max(lumA, lumB);
  const darker = Math.min(lumA, lumB);
  return (lighter + 0.05) / (darker + 0.05);
}

export function meetsContrastAA(
  foregroundHex: string,
  backgroundHex: string,
  isLargeText = false,
): boolean {
  const ratio = getContrastRatio(foregroundHex, backgroundHex);
  return ratio >= (isLargeText ? 3.0 : 4.5);
}
