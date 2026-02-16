"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FORMATS, getFormatLabel } from "@/lib/constants/config";
import { cn } from "@/lib/utils";
import { FormatKey, useFormatStore } from "@/store/use-format-store";

interface FormatSelectorProps {
  className?: string;
}

export function FormatSelector({ className }: FormatSelectorProps) {
  const { currentFormat, setFormat } = useFormatStore();

  return (
    <Select
      value={currentFormat}
      onValueChange={(val) => setFormat(val as FormatKey)}
    >
      <SelectTrigger className={cn("w-full", className)}>
        <SelectValue placeholder="Format" />
      </SelectTrigger>
      <SelectContent>
        {Object.keys(FORMATS).map((key) => (
          <SelectItem key={key} value={key}>
            {getFormatLabel(key)}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
