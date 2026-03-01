import { DEFAULT_THEME } from "@/lib/constants/config";
import { useThemeStore } from "@/store/use-theme-store";
import { City } from "@/types/city";
import { useMemo, useState } from "react";

export function useCityFilters(cities: City[]) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCountry, setSelectedCountry] = useState<string>("all");
  const [selectedRegion, setSelectedRegion] = useState<string>("all");
  const [selectedDepartment, setSelectedDepartment] = useState<string>("all");

  const setTheme = useThemeStore((state) => state.setTheme);

  // Extract unique values for filters
  const countries = useMemo(() => {
    const unique = new Set(
      cities
        .map((city) => city.admin_info?.structured?.country)
        .filter(Boolean) as string[],
    );
    return Array.from(unique).sort();
  }, [cities]);

  const regions = useMemo(() => {
    const unique = new Set(
      cities
        .filter(
          (city) =>
            selectedCountry === "all" ||
            city.admin_info?.structured?.country === selectedCountry,
        )
        .map((city) => city.admin_info?.structured?.state)
        .filter(Boolean) as string[],
    );
    return Array.from(unique).sort();
  }, [cities, selectedCountry]);

  const departments = useMemo(() => {
    const unique = new Set(
      cities
        .filter(
          (city) =>
            selectedRegion === "all" ||
            city.admin_info?.structured?.state === selectedRegion,
        )
        .filter(
          (city) =>
            selectedCountry === "all" ||
            city.admin_info?.structured?.country === selectedCountry,
        )
        .map((city) => city.admin_info?.structured?.county)
        .filter(Boolean) as string[],
    );
    return Array.from(unique).sort();
  }, [cities, selectedCountry, selectedRegion]);

  const filteredCities = useMemo(() => {
    return cities.filter((city) => {
      const matchesSearch = city.name
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
      const matchesCountry =
        selectedCountry === "all" ||
        city.admin_info?.structured?.country === selectedCountry;
      const matchesRegion =
        selectedRegion === "all" ||
        city.admin_info?.structured?.state === selectedRegion;
      const matchesDepartment =
        selectedDepartment === "all" ||
        city.admin_info?.structured?.county === selectedDepartment;

      return (
        matchesSearch && matchesCountry && matchesRegion && matchesDepartment
      );
    });
  }, [
    cities,
    searchQuery,
    selectedCountry,
    selectedRegion,
    selectedDepartment,
  ]);

  // Reset dependent filters when parent filter changes
  const handleCountryChange = (value: string) => {
    setSelectedCountry(value);
    setSelectedRegion("all");
    setSelectedDepartment("all");
  };

  const handleRegionChange = (value: string) => {
    setSelectedRegion(value);
    setSelectedDepartment("all");
  };

  const resetFilters = () => {
    setSearchQuery("");
    setSelectedCountry("all");
    setSelectedRegion("all");
    setSelectedDepartment("all");
    setTheme(DEFAULT_THEME);
  };

  return {
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
  };
}
