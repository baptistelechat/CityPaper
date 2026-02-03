import { cn } from "@/lib/utils";
import { City } from "@/types/city";
import Image from "next/image";
import Link from "next/link";

interface CityCardProps {
  city: City;
  className?: string;
}

export function CityCard({ city, className }: CityCardProps) {
  return (
    <Link
      href={`/city/${city.id}`}
      className={cn(
        "group relative aspect-5/7 overflow-hidden bg-muted block",
        className,
      )}
    >
      <Image
        src={city.image}
        alt={city.name}
        fill
        className="object-cover transition-transform duration-500 group-hover:scale-105"
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      />
      <div className="absolute inset-0 bg-linear-to-t from-black/60 via-transparent to-transparent" />
      <div className="absolute bottom-0 left-0 p-6 text-white">
        <h3 className="text-2xl font-bold tracking-tight">{city.name}</h3>
        <p className="text-sm font-medium text-white/90 uppercase tracking-wider">
          {city.country}
        </p>
      </div>
    </Link>
  );
}
