import countries from "i18n-iso-countries";
import en from "i18n-iso-countries/langs/en.json";
import fr from "i18n-iso-countries/langs/fr.json";

// Register locales
countries.registerLocale(fr);
countries.registerLocale(en);

/**
 * Get ISO 3166-1 alpha-2 code from country name (e.g. "France" -> "fr")
 * Tries French first, then English.
 */
export function getCountryCode(countryName: string): string | null {
  if (!countryName) return null;

  // Try to find code from French name
  let code = countries.getAlpha2Code(countryName, "fr");

  // Fallback to English if not found
  if (!code) {
    code = countries.getAlpha2Code(countryName, "en");
  }

  return code ? code.toLowerCase() : null;
}
