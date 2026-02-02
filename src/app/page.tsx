import { CityCard } from "@/components/city-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import cities from "@/data/cities.json";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-50 flex items-center justify-between border-b bg-background/80 px-6 py-4 backdrop-blur-md md:px-12">
        <div className="text-xl font-black uppercase tracking-widest">
          CityPaper
        </div>
        <Button variant="outline" size="sm">
          Demander
        </Button>
      </header>

      <main className="flex-1">
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
            />
          </div>
        </section>

        {/* Grid Section */}
        <section className="container mx-auto px-4 pb-24 md:px-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:gap-8">
            {cities.map((city) => (
              <CityCard key={city.id} city={city} />
            ))}
          </div>
        </section>
      </main>

      {/* Simple Footer */}
      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        <p>&copy; {new Date().getFullYear()} CityPaper. All rights reserved.</p>
      </footer>
    </div>
  );
}
