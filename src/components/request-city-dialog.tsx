"use client";

import { submitCityRequest } from "@/app/actions/requests";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RequestFormValues, requestSchema } from "@/lib/validations/request";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, MapPin, Search } from "lucide-react";
import { useEffect, useState, useTransition } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Separator } from "./ui/separator";

interface OSMResult {
  place_id: number;
  display_name: string;
  address: {
    city?: string;
    town?: string;
    village?: string;
    municipality?: string;
    county?: string;
    state?: string;
    country?: string;
    postcode?: string;
  };
  lat: string;
  lon: string;
}

export function RequestCityDialog({ trigger }: { trigger?: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [osmResults, setOsmResults] = useState<OSMResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLocation, setSelectedLocation] = useState<OSMResult | null>(
    null,
  );

  // Debounce search
  useEffect(() => {
    const handleSearch = async () => {
      if (!searchQuery || searchQuery.length < 3) {
        setOsmResults([]);
        return;
      }

      setIsSearching(true);
      setSelectedLocation(null);

      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
            searchQuery,
          )}&format=json&addressdetails=1&limit=5&accept-language=fr`,
        );
        const data = await response.json();
        setOsmResults(data);
      } catch (error) {
        console.error("OSM Error:", error);
        toast.error("Erreur lors de la recherche OpenStreetMap");
      } finally {
        setIsSearching(false);
      }
    };

    const timer = setTimeout(() => {
      handleSearch();
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const form = useForm<RequestFormValues>({
    resolver: zodResolver(requestSchema),
    defaultValues: {
      city: "",
      country: "",
      email: "",
      postcode: "",
      county: "",
      state: "",
    },
  });

  const selectLocation = (result: OSMResult) => {
    // ...
    const city =
      result.address.city ||
      result.address.town ||
      result.address.village ||
      result.address.municipality ||
      "";
    const postcode = result.address.postcode || "";
    const country = result.address.country || "";
    const county = result.address.county || "";
    const state = result.address.state || "";

    form.setValue("city", city);
    form.setValue("postcode", postcode);
    form.setValue("country", country);
    form.setValue("county", county);
    form.setValue("state", state);

    setSelectedLocation(result);
    setOsmResults([]); // Clear results to show form
  };

  const onSubmit = (data: RequestFormValues) => {
    startTransition(async () => {
      const result = await submitCityRequest(data, selectedLocation || {});

      if (result.error) {
        toast.error(result.error);
      } else {
        toast.success(
          "Demande envoyée ! Vous serez notifié si vous avez fourni un email.",
        );
        setOpen(false);
        form.reset();
        setSearchQuery("");
        setSelectedLocation(null);
      }
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || <Button>Demander une ville</Button>}
      </DialogTrigger>
      <DialogContent className="sm:max-w-125 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Demander une ville</DialogTitle>
          <DialogDescription>
            Nous générons les villes à la demande. Recherchez votre ville
            ci-dessous.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* Search Section */}
          <div className="flex gap-2">
            <div className="relative w-full">
              <Input
                placeholder="Rechercher (ex: Paris, 75001)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pr-10"
              />
              <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                {isSearching ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </div>
            </div>
          </div>

          <Separator />

          {/* Results List */}
          {osmResults.length > 0 && (
            <div className="border rounded-md divide-y max-h-50 overflow-y-auto">
              {osmResults.map((result) => (
                <button
                  key={result.place_id}
                  className="w-full text-left p-2 hover:bg-muted text-sm flex items-center gap-2"
                  onClick={() => selectLocation(result)}
                >
                  <MapPin className="size-4 text-muted-foreground shrink-0" />
                  <span>{result.display_name}</span>
                </button>
              ))}
            </div>
          )}

          {/* Form */}
          {selectedLocation && (
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-4"
                noValidate
              >
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="postcode"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Code Postal</FormLabel>
                        <FormControl>
                          <Input {...field} disabled />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="city"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Ville</FormLabel>
                        <FormControl>
                          <Input {...field} disabled />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="county"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Département / Comté</FormLabel>
                        <FormControl>
                          <Input {...field} disabled />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="state"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Région / État</FormLabel>
                        <FormControl>
                          <Input {...field} disabled />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="country"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Pays</FormLabel>
                        <FormControl>
                          <Input {...field} disabled />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email (Optionnel)</FormLabel>
                      <FormControl>
                        <Input placeholder="Pour être notifié" {...field} />
                      </FormControl>
                      <FormDescription>
                        Utilisé <strong>uniquement</strong> pour vous prévenir
                        lorsque la carte est prête.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <DialogFooter>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setOpen(false);
                      setOsmResults([]);
                      setSelectedLocation(null);
                      setSearchQuery("");
                    }}
                  >
                    Annuler
                  </Button>
                  <Button type="submit" disabled={isPending}>
                    {isPending && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    Envoyer la demande
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
