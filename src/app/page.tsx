import { CityCatalog } from "@/components/city-catalog";
import { RequestCityDialog } from "@/components/request-city-dialog";
import { Button } from "@/components/ui/button";
import cities from "@/data/cities.json";

export default function Home() {
  return (
    <>
      {/* Header */}
      <header className="sticky top-0 z-50 flex h-16 items-center justify-between border-b bg-background/80 px-6 backdrop-blur-md md:px-12">
        <div className="text-xl font-black uppercase tracking-widest">
          CityPaper
        </div>
        <RequestCityDialog
          trigger={
            <Button>
              Demander une ville
            </Button>
          }
        />
      </header>

      <main className="flex-1">
        <CityCatalog cities={cities} />
      </main>
    </>
  );
}
