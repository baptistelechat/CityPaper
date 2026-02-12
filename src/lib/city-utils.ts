import { City } from "@/types/city";

export function getCityImageUrl(
  city: City,
  theme: string,
  format: string = "ISO_A3_Portrait"
): string {
  const base_url =
    "https://huggingface.co/datasets/baptistelechat/citypaper-maps/resolve/main";

  const structured = city.admin_info?.structured;
  const img_path = structured
    ? `${structured.country}/${structured.state}/${structured.county}/${structured?.postcode}/${structured.city}`
    : "img_path_error";

  // Use structured city name if available (matches worker logic), fallback to display name
  const cityName = city.admin_info?.structured?.city || city.name;
  
  // Construct filename: CityName-format-theme.png
  // CityName preserves case, format and theme are lowercase
  const filename = `${cityName}-${format.toLowerCase()}-${theme.toLowerCase()}.png`;

  return `${base_url}/${img_path}/${format}/${filename}`;
}
