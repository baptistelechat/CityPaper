import { cn } from "@/lib/utils";

export function CityDetailsSkeleton() {
  return (
    <div className="mx-auto max-w-6xl w-full">
      <div className="grid gap-8 lg:grid-cols-2 lg:gap-16 items-center">
        {/* Image Skeleton */}
        <div className="relative aspect-5/7 w-full overflow-hidden bg-muted animate-pulse shadow-2xl rounded-sm" />

        {/* Info Skeleton */}
        <div className="flex flex-col justify-center space-y-8">
          <div className="space-y-4">
            <div className="h-12 w-3/4 bg-muted animate-pulse rounded" />
            <div className="h-6 w-1/2 bg-muted animate-pulse rounded" />
            <div className="h-4 w-1/3 bg-muted animate-pulse rounded" />
          </div>

          <div className="space-y-4">
            <div className="p-8 bg-muted/30 border border-border">
              <div className="h-6 w-1/2 bg-muted animate-pulse rounded mb-6" />
              <div className="flex flex-col gap-4">
                <div className="h-12 w-full bg-muted animate-pulse rounded" />
                <div className="h-12 w-full bg-muted animate-pulse rounded" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function CityCardSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "relative aspect-5/7 overflow-hidden bg-muted animate-pulse rounded-sm",
        className
      )}
    >
      <div className="absolute bottom-0 left-0 p-6 w-full space-y-2">
        <div className="h-8 w-3/4 bg-muted-foreground/10 rounded" />
        <div className="h-5 w-1/2 bg-muted-foreground/10 rounded" />
      </div>
    </div>
  );
}

export function CityCatalogSkeleton() {
  return (
    <div className="container mx-auto grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <CityCardSkeleton key={i} />
      ))}
    </div>
  );
}
