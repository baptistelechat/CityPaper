import { City } from "@/types/city";

export function getCityImageUrl(
  city: City,
  theme: string,
  format: string = "ISO_A3_Portrait",
): string {
  const base_url =
    "https://huggingface.co/datasets/baptistelechat/citypaper-maps/resolve/main";

  const structured = city.admin_info?.structured;

  // Helper to match Python's clean_name logic
  // Python: "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in n]).strip()
  const cleanName = (n: string) => {
    if (!n) return "";
    // \p{L} matches any unicode letter, \p{N} any unicode number
    // We keep letters, numbers, spaces, dashes, underscores.
    // Everything else becomes an underscore.
    return n.replace(/[^\p{L}\p{N} \-_]/gu, "_").trim();
  };

  if (!structured) return "img_path_error";

  // Build path segments dynamically to match worker's skip-if-empty logic
  const pathParts = [
    structured.country,
    structured.state,
    structured.county,
    structured.postcode,
    structured.city,
  ].filter((p): p is string => !!p); // Filter out undefined/null/empty

  const encodedPath = pathParts
    .map((p) => encodeURIComponent(cleanName(p)))
    .join("/");

  // Filename construction
  const rawCityName = structured.city || city.name;
  const safeCityName = cleanName(rawCityName);
  const safeFormat = cleanName(format).toLowerCase();
  const safeTheme = cleanName(theme).toLowerCase();

  const filename = `${safeCityName}-${safeFormat}-${safeTheme}.png`;

  return `${base_url}/${encodedPath}/${encodeURIComponent(format)}/${encodeURIComponent(filename)}`;
}
