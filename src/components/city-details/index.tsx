"use client";

import { FormatSelector } from "@/components/format-selector";
import { ThemeSelector } from "@/components/theme-selector";
import { Button } from "@/components/ui/button";
import { useMounted } from "@/hooks/use-mounted";
import { getCityImageUrl } from "@/lib/city-utils";
import { DEFAULT_FORMAT, DEFAULT_THEME, FORMATS } from "@/lib/constants/config";
import { getCountryCode } from "@/lib/country-utils";
import { useFormatStore } from "@/store/use-format-store";
import { useThemeStore } from "@/store/use-theme-store";
import type { City } from "@/types/city";
import { Heart } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { ResetFiltersButton } from "../reset-filters-button";
import { CityDetailsSkeleton } from "../skeletons";
import { CityDetailsBadges } from "./components/city-details-badges";
import { DownloadButton } from "./components/download-button";

interface CityDetailsProps {
  city: City;
  suggestedCities: City[];
}

function CityImagePreview({
  imageUrl,
  alt,
}: {
  imageUrl: string;
  alt: string;
}) {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <>
      {isLoading && (
        <div className="absolute inset-0 bg-muted animate-pulse z-10" />
      )}
      <Image
        src={imageUrl}
        alt={alt}
        fill
        priority
        className={`object-cover transition-all duration-500 ${
          isLoading ? "scale-105 blur-sm" : "scale-100 blur-0"
        }`}
        sizes="(max-width: 768px) 100vw, 50vw"
        onLoadingComplete={() => setIsLoading(false)}
      />
    </>
  );
}

export function CityDetails({ city, suggestedCities }: CityDetailsProps) {
  const { currentTheme } = useThemeStore();
  const { currentFormat } = useFormatStore();
  const mounted = useMounted();

  // Show Skeleton Loader until mounted to prevent theme flash
  if (!mounted) {
    return <CityDetailsSkeleton />;
  }

  const activeTheme = currentTheme || DEFAULT_THEME;
  const activeFormat = currentFormat || DEFAULT_FORMAT;
  const imageUrl = getCityImageUrl(city, activeTheme, activeFormat);
  const countryCode = getCountryCode(city.country);

  // Calculate aspect ratio
  const formatData =
    FORMATS[activeFormat as keyof typeof FORMATS] || FORMATS[DEFAULT_FORMAT];
  const aspectRatio = formatData.w / formatData.h;

  return (
    <div className="mx-auto max-w-6xl w-full">
      <div className="grid gap-8 lg:grid-cols-2 lg:gap-16 items-center">
        {/* Image Section */}
        <div
          className="relative w-full overflow-hidden bg-muted shadow-2xl transition-all duration-500 ease-in-out"
          style={{ aspectRatio }}
        >
          <CityImagePreview
            key={imageUrl}
            imageUrl={imageUrl}
            alt={`${city.name} - CityPaper`}
          />
        </div>

        {/* Info Section */}
        <div className="flex flex-col justify-center space-y-8">
          <div>
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl uppercase">
              {city.name}
            </h1>
            <p className="mt-2 text-xl text-muted-foreground uppercase tracking-wider flex items-center gap-2">
              {countryCode && (
                <span className={`fi fi-${countryCode} rounded-sm shadow-sm`} />
              )}
              {city.country}
            </p>
            <p className="mt-1 text-sm text-muted-foreground/80 font-mono">
              {city.coordinates
                .split(",")
                .map((coord) => coord.trim() + "°")
                .join(", ")}
            </p>
            <CityDetailsBadges city={city} />
          </div>

          <div className="space-y-4">
            <div className="p-8 bg-muted/30 border border-border">
              <h3 className="font-semibold mb-6 text-lg uppercase tracking-wider">
                Télécharger l&apos;affiche
              </h3>
              <div className="flex flex-col gap-4">
                <div className="flex flex-col sm:flex-row gap-4">
                  <ThemeSelector className="flex-1" />
                  <FormatSelector className="flex-1" />
                  <ResetFiltersButton
                    className="w-full sm:w-10 shrink-0"
                    labelClassName="sm:hidden"
                  />
                </div>

                <DownloadButton
                  url={imageUrl}
                  filename={`${city.name.toLowerCase()}-poster-${activeTheme}-${activeFormat}.jpg`}
                  label="Télécharger"
                />
              </div>
              <p className="mt-6 text-xs text-muted-foreground border-t border-border/50 pt-4">
                Licence : ODbL (OpenStreetMap)
              </p>
            </div>
          </div>

          {/* Suggestions Section */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
              <Heart className="size-4" />
              Vous aimerez aussi
            </h3>
            <div className="flex flex-wrap gap-2 text-sm">
              {suggestedCities.map((suggested) => (
                <Button
                  key={suggested.id}
                  variant="link"
                  asChild
                  className="h-auto p-0 text-foreground"
                >
                  <Link href={`/city/${suggested.id}`}>[{suggested.name}]</Link>
                </Button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
