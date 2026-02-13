import { DEFAULT_THEME, MapTheme } from "@/lib/constants/config";
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface ThemeStore {
  currentTheme: MapTheme;
  setTheme: (theme: MapTheme) => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      currentTheme: DEFAULT_THEME, // Default to first available theme
      setTheme: (theme) => set({ currentTheme: theme }),
    }),
    {
      name: "city-paper-theme-storage",
    },
  ),
);
