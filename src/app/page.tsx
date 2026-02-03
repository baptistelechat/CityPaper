import { Button } from "@/components/ui/button";
import { CityCatalog } from "@/components/city-catalog";
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
        <CityCatalog cities={cities} />
      </main>

      {/* Simple Footer */}
      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        <p>&copy; {new Date().getFullYear()} CityPaper. All rights reserved.</p>
      </footer>
    </div>
  );
}
