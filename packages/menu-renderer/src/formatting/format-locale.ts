export function normalizeLocale(locale?: string): string {
  if (!locale) return "en-IN";
  const trimmed = locale.trim();
  if (!/^[a-z]{2}(-[A-Z]{2})?$/.test(trimmed)) {
    return "en-IN";
  }
  return trimmed;
}

export function getTextDirection(locale: string): "ltr" | "rtl" {
  const rtlLocales = ["ar", "he", "fa", "ur"];
  const lang = locale.split("-")[0].toLowerCase();
  return rtlLocales.includes(lang) ? "rtl" : "ltr";
}
