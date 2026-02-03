"use client";

import { CityCard } from "@/components/city-card";
import { Input } from "@/components/ui/input";
import type { City } from "@/types/city";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";

interface CityCatalogProps {
  cities: City[];
}

export function CityCatalog({ cities }: CityCatalogProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredCities = cities.filter((city) =>
    city.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <>
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center gap-8 px-4 py-20 text-center md:py-32">
        <h1 className="max-w-4xl text-4xl font-black uppercase tracking-tighter md:text-6xl lg:text-7xl">
          Cartes minimalistes <br className="hidden md:block" /> pour vos murs
        </h1>

        <div className="w-full max-w-md">
          <Input
            type="search"
            placeholder="Rechercher votre ville..."
            className="h-12 text-lg shadow-sm"
            aria-label="Rechercher une ville"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </section>

      {/* Grid Section */}
      <section className="container mx-auto px-4 pb-24 md:px-6">
        <motion.div
          className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:gap-8"
          layout
        >
          <AnimatePresence mode="popLayout">
            {filteredCities.map((city) => (
              <motion.div
                key={city.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.2 }}
              >
                <CityCard city={city} />
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>

        {filteredCities.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <p className="text-xl text-muted-foreground">
              Aucune ville trouvée
            </p>
          </motion.div>
        )}
      </section>
    </>
  );
}
