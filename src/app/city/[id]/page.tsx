import { DownloadButton } from "@/components/download-button";
import { Button } from "@/components/ui/button";
import cities from "@/data/cities.json";
import { ArrowLeft, Heart } from "lucide-react";
import type { Metadata } from "next";
import Image from "next/image";
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
  ];

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
        <Button variant="outline" size="sm">
          Demander
        </Button>
      </header>

      <main className="flex-1 flex flex-col justify-center p-6 md:p-12">
        <div className="mx-auto max-w-6xl w-full">
          <div className="grid gap-8 lg:grid-cols-2 lg:gap-16 items-center">
            {/* Image Section */}
            <div className="relative aspect-5/7 w-full overflow-hidden bg-muted shadow-2xl">
              <Image
                src={city.image}
                alt={`${city.name} - CityPaper`}
                fill
                priority
                className="object-cover"
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
                  {city.coordinates}
                </p>
              </div>

              <div className="space-y-4">
                <div className="p-8 bg-muted/30 border border-border">
                  <h3 className="font-semibold mb-6 text-lg uppercase tracking-wider">
                    Télécharger l&apos;affiche
                  </h3>
                  <div className="flex flex-col gap-4">
                    <DownloadButton
                      url={city.image}
                      filename={`${city.name.toLowerCase()}-poster.jpg`}
                      label="Télécharger PDF (Print)"
                    />
                    <DownloadButton
                      url={city.image}
                      filename={`${city.name.toLowerCase()}-wallpaper.jpg`}
                      label="Télécharger Wallpaper"
                      variant="outline"
                    />
                  </div>
                  <p className="mt-6 text-xs text-muted-foreground border-t border-border/50 pt-4">
                    Licence : ODbL (OpenStreetMap)
                  </p>
                </div>
              </div>

              {/* Suggestions Section - Moved here */}
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
                      <Link href={`/city/${suggested.id}`}>
                        [{suggested.name}]
                      </Link>
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
