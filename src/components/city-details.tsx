"use client";

import { DownloadButton } from "@/components/download-button";
import { CityDetailsSkeleton } from "@/components/skeletons";
import { Button } from "@/components/ui/button";
import { useMounted } from "@/hooks/use-mounted";
import { getCityImageUrl } from "@/lib/city-utils";
import { DEFAULT_THEME, getThemeLabel } from "@/lib/constants/config";
import { useThemeStore } from "@/store/use-theme-store";
import type { City } from "@/types/city";
import { Heart } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

interface CityDetailsProps {
  city: City;
  suggestedCities: City[];
}

export function CityDetails({ city, suggestedCities }: CityDetailsProps) {
  const { currentTheme } = useThemeStore();
  const mounted = useMounted();

  // Show Skeleton Loader until mounted to prevent theme flash
  if (!mounted) {
    return <CityDetailsSkeleton />;
  }

  const activeTheme = currentTheme || DEFAULT_THEME;
  const imageUrl = getCityImageUrl(city, activeTheme);

  return (
    <div className="mx-auto max-w-6xl w-full">
      <div className="grid gap-8 lg:grid-cols-2 lg:gap-16 items-center">
        {/* Image Section */}
        <div className="relative aspect-5/7 w-full overflow-hidden bg-muted shadow-2xl">
          <Image
            src={imageUrl}
            alt={`${city.name} - CityPaper`}
            fill
            priority
            className="object-cover transition-all duration-500"
            sizes="(max-width: 768px) 100vw, 50vw"
          />
        </div>

        {/* Info Section */}
        <div className="flex flex-col justify-center space-y-8">
          <div>
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl uppercase">
              {city.name}
            </h1>
            <p className="mt-2 text-xl text-muted-foreground uppercase tracking-wider">
              {city.country}
            </p>
            <p className="mt-1 text-sm text-muted-foreground/80 font-mono">
              {city.coordinates
                .split(",")
                .map((coord) => coord.trim() + "°")
                .join(", ")}
            </p>
          </div>

          <div className="space-y-4">
            <div className="p-8 bg-muted/30 border border-border">
              <h3 className="font-semibold mb-6 text-lg uppercase tracking-wider">
                Télécharger l&apos;affiche
              </h3>
              <div className="flex flex-col gap-4">
                <DownloadButton
                  url={imageUrl}
                  filename={`${city.name.toLowerCase()}-poster-${activeTheme}.jpg`}
                  label="Télécharger PDF (Print)"
                />
                <DownloadButton
                  url={imageUrl}
                  filename={`${city.name.toLowerCase()}-wallpaper-${activeTheme}.jpg`}
                  label="Télécharger Wallpaper"
                  variant="outline"
                />
              </div>
              <p className="mt-6 text-xs text-muted-foreground border-t border-border/50 pt-4">
                Licence : ODbL (OpenStreetMap) • Thème :{" "}
                {getThemeLabel(activeTheme)}
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
