import { CityDetails } from "@/components/city-details";
import { RequestCityDialog } from "@/components/request-city-dialog";
import { Button } from "@/components/ui/button";
import cities from "@/data/cities.json";
import { ArrowLeft } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

export async function generateStaticParams() {
  return cities.map((city) => ({
    id: city.id,
  }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const city = cities.find((c) => c.id === id);

  if (!city) {
    return {
      title: "Ville non trouvée",
    };
  }

  return {
    title: `CityPaper | ${city.name} | ${city.country}`,
    description: `Affiche minimaliste de ${city.name}, ${city.country}. Téléchargez le poster ou le fond d'écran.`,
  };
}

export default async function CityPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const city = cities.find((c) => c.id === id);

  if (!city) {
    notFound();
  }

  // Suggest next 3 cities (or first 3 if at end)
  const currentIndex = cities.findIndex((c) => c.id === id);
  const suggestedCities = [
    cities[(currentIndex + 1) % cities.length],
    cities[(currentIndex + 2) % cities.length],
    cities[(currentIndex + 3) % cities.length],
  ].filter(
    (c, index, self) =>
      // Filter out undefined and duplicates
      c && self.findIndex((t) => t.id === c.id) === index && c.id !== id,
  );

  return (
    <>
      <header className="sticky top-0 z-50 flex h-16 items-center justify-between border-b bg-background/80 px-6 backdrop-blur-md md:px-12">
        <Button
          variant="link"
          asChild
          className="pl-0 text-muted-foreground hover:text-foreground"
        >
          <Link href="/">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Retour à la galerie
          </Link>
        </Button>
        <RequestCityDialog trigger={<Button>Demander une ville</Button>} />
      </header>

      <main className="flex-1 flex flex-col justify-center p-6 md:p-12">
        <CityDetails city={city} suggestedCities={suggestedCities} />
      </main>
    </>
  );
}
