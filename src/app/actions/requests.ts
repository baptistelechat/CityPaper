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

  const { city, country, email, county, state, postcode } = result.data;

  try {
    const { error } = await supabase.from("requests").insert({
      city,
      country,
      email: email || null,
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
