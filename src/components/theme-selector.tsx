"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MAP_THEMES, MapTheme } from "@/lib/constants/config";
import { cn } from "@/lib/utils";
import { useThemeStore } from "@/store/use-theme-store";

interface ThemeSelectorProps {
  className?: string;
}

export function ThemeSelector({ className }: ThemeSelectorProps) {
  const { currentTheme, setTheme } = useThemeStore();

  return (
    <Select
      value={currentTheme}
      onValueChange={(val) => setTheme(val as MapTheme)}
    >
      <SelectTrigger className={cn("w-full", className)}>
        <SelectValue placeholder="Thème" />
      </SelectTrigger>
      <SelectContent>
        {MAP_THEMES.map((theme) => (
          <SelectItem key={theme.value} value={theme.value}>
            {theme.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
