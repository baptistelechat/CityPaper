import { DEFAULT_FORMAT, FORMATS } from "@/lib/constants/config";
import { create } from "zustand";
import { persist } from "zustand/middleware";

export type FormatKey = keyof typeof FORMATS;

interface FormatStore {
  currentFormat: FormatKey;
  setFormat: (format: FormatKey) => void;
}

export const useFormatStore = create<FormatStore>()(
  persist(
    (set) => ({
      currentFormat: DEFAULT_FORMAT,
      setFormat: (format) => set({ currentFormat: format }),
    }),
    {
      name: "city-paper-format-storage",
    },
  ),
);
