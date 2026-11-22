/**
 * ModularMenu — Monetary Formatting (ARC-09 §9.1).
 * Uses canonical minor-unit currency precision with standard Intl.NumberFormat.
 */

const CURRENCY_PRECISIONS: Record<string, number> = {
  INR: 2,
  USD: 2,
  EUR: 2,
  GBP: 2,
  JPY: 0,
  KWD: 3,
  BHD: 3,
  OMR: 3,
};

export function getCurrencyPrecision(currency: string): number {
  const upper = (currency || "").toUpperCase();
  return CURRENCY_PRECISIONS[upper] !== undefined ? CURRENCY_PRECISIONS[upper] : 2;
}

export function formatPrice(
  amountMinor: number,
  currency: string,
  locale: string = "en-IN",
  minorUnitDigits?: number
): string {
  if (!Number.isSafeInteger(amountMinor) || amountMinor < 0) {
    throw new Error("INVALID_MONEY_AMOUNT");
  }

  const digits = minorUnitDigits !== undefined ? minorUnitDigits : getCurrencyPrecision(currency);
  if (!Number.isInteger(digits) || digits < 0 || digits > 3) {
    throw new Error("INVALID_CURRENCY_PRECISION");
  }

  const amount = amountMinor / Math.pow(10, digits);
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(amount);
}
