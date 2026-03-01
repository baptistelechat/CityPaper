"use client";

import { Button, ButtonProps } from "@/components/ui/button";
import { DEFAULT_FORMAT, DEFAULT_THEME } from "@/lib/constants/config";
import { cn } from "@/lib/utils";
import { useFormatStore } from "@/store/use-format-store";
import { useThemeStore } from "@/store/use-theme-store";
import { RotateCcw } from "lucide-react";

interface ResetFiltersButtonProps extends ButtonProps {
  onReset?: () => void;
  isFiltered?: boolean;
  labelClassName?: string;
}

export function ResetFiltersButton({
  onReset,
  isFiltered = false,
  className,
  labelClassName,
  variant = "outline",
  size = "icon",
  ...props
}: ResetFiltersButtonProps) {
  const { currentTheme, setTheme } = useThemeStore();
  const { currentFormat, setFormat } = useFormatStore();

  const isThemeChanged = currentTheme !== DEFAULT_THEME;
  const isFormatChanged = currentFormat !== DEFAULT_FORMAT;

  const hasChanges = isFiltered || isThemeChanged || isFormatChanged;

  const handleReset = () => {
    setTheme(DEFAULT_THEME);
    setFormat(DEFAULT_FORMAT);
    onReset?.();
  };

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleReset}
      disabled={!hasChanges}
      className={cn("shrink-0", className)}
      title="Réinitialiser les filtres"
      {...props}
    >
      <RotateCcw className="h-4 w-4" />
      <span className={cn("ml-2", labelClassName)}>Réinitialiser</span>
    </Button>
  );
}
