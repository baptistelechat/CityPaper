"use server";

import { supabase } from "@/lib/supabase";
import { RequestFormValues, requestSchema } from "@/lib/validations/request";

export async function submitCityRequest(
  data: RequestFormValues,
  osmData?: object,
) {
  const result = requestSchema.safeParse(data);

  if (!result.success) {
    return { error: "Données invalides" };
  }

  const { city, country, county, state, postcode } = result.data;

  try {
    const { error } = await supabase.from("requests").insert({
      city,
      country,
      county: county || null,
      state: state || null,
      postcode,
      status: "pending",
      metadata: osmData || {},
    });

    if (error) {
      console.error("Supabase error:", error);
      return {
        error: "Erreur lors de l'envoi de la demande. Veuillez réessayer.",
      };
    }

    return { success: true };
  } catch (err) {
    console.error("Unexpected error:", err);
    return { error: "Une erreur inattendue est survenue." };
  }
}

export async function searchCity(query: string) {
  if (!query || query.length < 3) return [];

  try {
    // Basic CSV/verbose input detection
    // Expected format: "City,Country,Region,Dept,Postcode" or variations
    const parts = query.split(",").map((p) => p.trim());
    let optimizedQuery = query;
    let extractedPostcode = "";

    // If we have multiple parts (CSV-like)
    if (parts.length > 2) {
      // Find postcode (usually 5 digits in France, but let's be generic 4-6 digits)
      const postcodeIndex = parts.findIndex((p) => /^\d{4,6}$/.test(p));
      if (postcodeIndex !== -1) {
        extractedPostcode = parts[postcodeIndex];
      }

      // Construct optimized query: "City, Postcode" or "City, Country"
      // Assume first part is City
      const city = parts[0];
      // Assume second part is Country if it's not a postcode/region
      const potentialCountry = parts[1];

      if (extractedPostcode) {
        optimizedQuery = `${city}, ${extractedPostcode}`;
        // If we have a country, append it for precision, unless it's the postcode itself
        if (potentialCountry && potentialCountry !== extractedPostcode) {
           optimizedQuery += `, ${potentialCountry}`;
        }
      } else if (potentialCountry) {
        optimizedQuery = `${city}, ${potentialCountry}`;
      }
    }

    const params = new URLSearchParams({
      q: optimizedQuery,
      format: "json",
      addressdetails: "1",
      limit: "5",
      "accept-language": "fr",
    });

    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?${params.toString()}`,
      {
        headers: {
          "User-Agent": "CityPaperRequest/1.0 (contact@citypaper.app)", // Replace with actual app info
        },
      },
    );

    if (!response.ok) {
      throw new Error(`Nominatim error: ${response.statusText}`);
    }

    const data = await response.json();

    // Filter results to ensure we have the minimum required data (City, Country, Postcode)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const validResults = data.filter((item: any) => {
      const address = item.address;
      if (!address) return false;

      // Inject extracted postcode if missing from API result
      if (!address.postcode && extractedPostcode) {
        address.postcode = extractedPostcode;
      }

      const hasCity =
        address.city ||
        address.town ||
        address.village ||
        address.municipality ||
        address.hamlet ||
        address.suburb ||
        address.administrative ||
        address.county; // Last resort fallback

      const hasCountry = address.country;
      // We can be strict about postcode since it's required by the schema
      const hasPostcode = address.postcode;

      return hasCity && hasCountry && hasPostcode;
    });

    return validResults;
  } catch (error) {
    console.error("Search error:", error);
    return [];
  }
}
