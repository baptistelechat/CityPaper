export const SELECTED_THEMES = [
  // "autumn",
  "blueprint",
  // "contrast_zones",
  // "copper_patina",
  // "emerald",
  "forest",
  // "gradient_roads",
  "japanese_ink",
  "midnight_blue",
  // "monochrome_blue",
  // "neon_cyberpunk",
  "noir",
  "ocean",
  "pastel_dream",
  // "sunset",
  "terracotta",
  "warm_beige",
] as const;

export type MapTheme = (typeof SELECTED_THEMES)[number];

export const DEFAULT_THEME: MapTheme = "pastel_dream";

export const getThemeLabel = (theme: string) => {
  return theme
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

export const MAP_THEMES = SELECTED_THEMES.map((theme) => ({
  value: theme,
  label: getThemeLabel(theme),
}));

export const FORMATS = {
  // ISO Formats (Standard: A3)
  // A2 (16.5 x 23.4") is too big. A3 is the largest standard fitting 20".
  // Ratio: ~1.41 (√2) - Very close to 5:7 (1.40) -> Redundant
  ISO_A3_Landscape: { w: 16.5, h: 11.7 }, // 42.0 x 29.7 cm | Ratio 1.41
  ISO_A3_Portrait: { w: 11.7, h: 16.5 }, // 29.7 x 42.0 cm | Ratio 1.41

  // Standard Photo Ratios (Largest Standard Size < 20")

  // 2:3 Ratio -> 12x18" (Standard Poster)
  // Ratio: 1.50 - Distinctly taller/wider
  Photo_12x18_Portrait: { w: 12.0, h: 18.0 }, // 30.5 x 45.7 cm | Ratio 1.50
  Photo_18x12_Landscape: { w: 18.0, h: 12.0 }, // 45.7 x 30.5 cm | Ratio 1.50

  // 3:4 Ratio -> 15x20" (Fits exactly)
  // Ratio: 1.33 - "Middle ground" between 2:3 (1.5) and 4:5 (1.25)
  // "Photo_15x20_Portrait": {"w": 15.0, "h": 20.0},  // 38.1 x 50.8 cm | Ratio 1.33
  // "Photo_20x15_Landscape": {"w": 20.0, "h": 15.0}, // 50.8 x 38.1 cm | Ratio 1.33

  // 4:5 Ratio -> 16x20" (Standard Frame)
  // Ratio: 1.25 - Boxier/Compact
  Photo_16x20_Portrait: { w: 16.0, h: 20.0 }, // 40.6 x 50.8 cm | Ratio 1.25
  Photo_20x16_Landscape: { w: 20.0, h: 16.0 }, // 50.8 x 40.6 cm | Ratio 1.25

  // 5:7 Ratio -> 10x14" (2x 5x7")
  // Ratio: 1.40 - Almost identical to ISO (1.41) -> Redundant
  // "Frame_10x14_Portrait": {"w": 10.0, "h": 14.0}, // 25.4 x 35.6 cm | Ratio 1.40
  // "Frame_14x10_Landscape": {"w": 14.0, "h": 10.0}, // 35.6 x 25.4 cm | Ratio 1.40

  // Screen Formats (Standard Resolutions @ 300 DPI)
  // Ratio: ~1.78 (16:9) - Panoramic
  Wallpaper_5K_PC: { w: 17.07, h: 9.6 }, // 43.4 x 24.4 cm | Ratio 1.78
  Wallpaper_5K_Mobile: { w: 9.6, h: 17.07 }, // 24.4 x 43.4 cm | Ratio 1.78

  // Social / Square (Standard 20x20")
  // Ratio: 1.00
  Square_20x20: { w: 20.0, h: 20.0 }, // 50.8 x 50.8 cm | Ratio 1.00
};

export const DEFAULT_FORMAT: keyof typeof FORMATS = "ISO_A3_Portrait";

export const getFormatLabel = (key: string) => {
  const format = FORMATS[key as keyof typeof FORMATS];
  if (!format) return key;
  // Convert underscores to spaces and add dimensions
  const name = key.replace(/_/g, " ");
  return `${name} (${format.w}x${format.h}")`;
};
