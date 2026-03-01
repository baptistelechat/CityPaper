import { ResetFiltersButton } from "@/components/reset-filters-button";
import { ThemeSelector } from "@/components/theme-selector";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCityFilters } from "@/hooks/use-city-filters";
import { DEFAULT_THEME } from "@/lib/constants/config";
import { useThemeStore } from "@/store/use-theme-store";
import type { City } from "@/types/city";
import { X } from "lucide-react";
import { ReactNode } from "react";

interface CityCatalogControlsProps {
  cities: City[];
  children: (filteredCities: City[]) => ReactNode;
}

export function CityCatalogControls({
  cities,
  children,
}: CityCatalogControlsProps) {
  const { currentTheme } = useThemeStore();

  const {
    searchQuery,
    setSearchQuery,
    selectedCountry,
    handleCountryChange,
    selectedRegion,
    handleRegionChange,
    selectedDepartment,
    setSelectedDepartment,
    resetFilters,
    countries,
    regions,
    departments,
    filteredCities,
  } = useCityFilters(cities);

  const filteredCount = filteredCities.length;
  const isFiltered = Boolean(
    searchQuery ||
    selectedCountry !== "all" ||
    selectedRegion !== "all" ||
    selectedDepartment !== "all" ||
    currentTheme !== DEFAULT_THEME,
  );

  return (
    <div className="flex flex-col w-full gap-8">
      <div className="flex flex-col w-full max-w-4xl mx-auto gap-4">
        <div className="w-full max-w-md mx-auto flex flex-col gap-2">
          <div className="relative">
            <Input
              type="search"
              placeholder="Rechercher votre ville..."
              className="h-12 text-lg shadow-sm pr-10"
              aria-label="Rechercher une ville"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          <div className="flex items-center justify-end px-1">
            <span className="text-sm text-muted-foreground">
              {filteredCount} résultat{filteredCount > 1 ? "s" : ""}
            </span>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-2 w-full items-start lg:items-center">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 w-full">
            <Select value={selectedCountry} onValueChange={handleCountryChange}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Pays" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les pays</SelectItem>
                {countries.map((country) => (
                  <SelectItem key={country} value={country}>
                    {country}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select
              value={selectedRegion}
              onValueChange={handleRegionChange}
              disabled={selectedCountry === "all" && regions.length === 0}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Région" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes les régions</SelectItem>
                {regions.map((region) => (
                  <SelectItem key={region} value={region}>
                    {region}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select
              value={selectedDepartment}
              onValueChange={setSelectedDepartment}
              disabled={selectedRegion === "all" && departments.length === 0}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Département" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les départements</SelectItem>
                {departments.map((dept) => (
                  <SelectItem key={dept} value={dept}>
                    {dept}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <ThemeSelector />
          </div>
          <ResetFiltersButton
            onReset={resetFilters}
            isFiltered={isFiltered}
            className="w-full sm:w-10 shrink-0"
            labelClassName="sm:hidden"
          />
        </div>
      </div>

      {children(filteredCities)}
    </div>
  );
}
