"use client";

import { RequestCityDialog } from "@/components/features/request-city-dialog";
import { CityCatalogSkeleton } from "@/components/skeletons";
import { useMounted } from "@/hooks/use-mounted";
import type { City } from "@/types/city";
import { AnimatePresence, motion } from "framer-motion";
import { CityCard } from "./components/city-card";
import { CityCatalogControls } from "./components/city-catalog-controls";

interface CityCatalogProps {
  cities: City[];
}

export function CityCatalog({ cities }: CityCatalogProps) {
  const mounted = useMounted();

  return (
    <>
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center gap-8 px-4 py-20 text-center md:py-32">
        <h1 className="max-w-4xl text-4xl font-black uppercase tracking-tighter md:text-6xl lg:text-7xl">
          Cartes minimalistes <br className="hidden md:block" /> pour vos murs
        </h1>

        <div className="flex flex-col w-full gap-4">
          <CityCatalogControls cities={cities}>
            {(filteredCities) =>
              !mounted ? (
                <CityCatalogSkeleton />
              ) : (
                <div className="container mx-auto grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
                  <AnimatePresence>
                    {filteredCities.map((city) => (
                      <motion.div
                        key={city.id}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        transition={{ duration: 0.2 }}
                        layout
                      >
                        <CityCard city={city} />
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              )
            }
          </CityCatalogControls>
        </div>
      </section>

      {/* Request City Section */}
      <section className="bg-muted/30 py-20">
        <div className="flex flex-col items-center justify-center gap-4 text-center">
          <h2 className="text-2xl font-bold">
            Vous ne trouvez pas votre ville ?
          </h2>
          <RequestCityDialog />
        </div>
      </section>
    </>
  );
}
