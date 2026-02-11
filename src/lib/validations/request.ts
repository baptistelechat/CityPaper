import { z } from "zod";

export const requestSchema = z.object({
  city: z.string().min(1, "La ville est requise"),
  country: z.string().min(1, "Le pays est requis"),
  email: z.string().email("Email invalide").optional().or(z.literal("")),
  // Hidden fields filled by OSM selection
  county: z.string().optional(),
  state: z.string().optional(),
  postcode: z.string().min(1, "Le code postal est requis"),
});

export type RequestFormValues = z.infer<typeof requestSchema>;
