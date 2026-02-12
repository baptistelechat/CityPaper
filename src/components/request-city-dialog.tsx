"use client";

import { searchCity, submitCityRequest } from "@/app/actions/requests";
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
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RequestFormValues, requestSchema } from "@/lib/validations/request";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  AlertCircle,
  CheckCircle2,
  Loader2,
  MapPin,
  Search,
  Trash2,
  XCircle,
} from "lucide-react";
import { useEffect, useState, useTransition } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Select, SelectContent, SelectItem, SelectTrigger } from "./ui/select";
import { Separator } from "./ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Textarea } from "./ui/textarea";

interface OSMResult {
  place_id: number;
  display_name: string;
  address: {
    city?: string;
    town?: string;
    village?: string;
    municipality?: string;
    hamlet?: string;
    suburb?: string;
    administrative?: string;
    county?: string;
    state?: string;
    country?: string;
    postcode?: string;
  };
  lat: string;
  lon: string;
}

interface BulkItem {
  id: string;
  originalQuery: string;
  status:
    | "pending"
    | "searching"
    | "found"
    | "ambiguous"
    | "not_found"
    | "error"
    | "submitted";
  results: OSMResult[];
  selectedResult?: OSMResult;
  error?: string;
}

export function RequestCityDialog({ trigger }: { trigger?: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [isPending, startTransition] = useTransition();

  // Single Search State
  const [osmResults, setOsmResults] = useState<OSMResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLocation, setSelectedLocation] = useState<OSMResult | null>(
    null,
  );

  // Bulk Import State
  const [bulkInput, setBulkInput] = useState("");
  const [bulkItems, setBulkItems] = useState<BulkItem[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState("single");

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
        const data = await searchCity(searchQuery);
        setOsmResults(data as OSMResult[]);
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
      result.address.hamlet ||
      result.address.suburb ||
      result.address.administrative ||
      result.address.county ||
      result.display_name.split(",")[0];
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

  const analyzeBulkInput = async () => {
    const lines = bulkInput
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.length > 0);
    if (lines.length === 0) return;

    setIsAnalyzing(true);
    const initialItems: BulkItem[] = lines.map((line) => ({
      id: Math.random().toString(36).substring(7),
      originalQuery: line,
      status: "pending",
      results: [],
    }));
    setBulkItems(initialItems);

    // Process items sequentially to avoid rate limiting
    const updatedItems = [...initialItems];

    for (let i = 0; i < updatedItems.length; i++) {
      const item = updatedItems[i];
      item.status = "searching";
      setBulkItems([...updatedItems]);

      try {
        // Add delay for rate limiting (1s)
        if (i > 0) await new Promise((resolve) => setTimeout(resolve, 1000));

        const data: OSMResult[] = (await searchCity(
          item.originalQuery,
        )) as OSMResult[];

        // Deduplicate results based on display_name
        const uniqueResults = data.filter(
          (result, index, self) =>
            index ===
            self.findIndex((r) => r.display_name === result.display_name),
        );

        item.results = uniqueResults;
        if (uniqueResults.length === 0) {
          item.status = "not_found";
        } else if (uniqueResults.length === 1) {
          item.status = "found";
          item.selectedResult = uniqueResults[0];
        } else {
          item.status = "ambiguous";
          item.selectedResult = uniqueResults[0]; // Pre-select first
        }
      } catch (error) {
        console.error("Bulk Search Error:", error);
        item.status = "error";
        item.error = "Erreur réseau";
      }

      setBulkItems([...updatedItems]);
    }

    setIsAnalyzing(false);
  };

  const submitBulkItems = () => {
    startTransition(async () => {
      const validItems = bulkItems.filter(
        (item) =>
          (item.status === "found" || item.status === "ambiguous") &&
          item.selectedResult,
      );

      if (validItems.length === 0) {
        toast.error("Aucune ville valide à envoyer.");
        return;
      }

      let successCount = 0;
      const updatedItems = [...bulkItems];

      for (const item of validItems) {
        if (!item.selectedResult) continue;

        const result = item.selectedResult;
        const formData: RequestFormValues = {
          city:
            result.address.city ||
            result.address.town ||
            result.address.village ||
            result.address.municipality ||
            result.address.hamlet ||
            result.address.suburb ||
            result.address.administrative ||
            result.address.county ||
            result.display_name.split(",")[0],
          postcode: result.address.postcode || "",
          country: result.address.country || "",
          county: result.address.county || "",
          state: result.address.state || "",
        };

        // Basic validation before submit
        if (!formData.city || !formData.country || !formData.postcode) {
          item.error = "Données incomplètes (Ville/Pays/CP manquants)";
          item.status = "error";
          continue;
        }

        const submitResult = await submitCityRequest(formData, result);

        const index = updatedItems.findIndex((i) => i.id === item.id);
        if (index !== -1) {
          if (submitResult.error) {
            updatedItems[index].status = "error";
            updatedItems[index].error = submitResult.error;
          } else {
            updatedItems[index].status = "submitted";
            successCount++;
          }
        }
        setBulkItems([...updatedItems]);
      }

      toast.success(`${successCount} demandes envoyées avec succès !`);
      if (successCount === validItems.length) {
        // Optional: Clear or close if all successful
        // setBulkInput("");
        // setBulkItems([]);
      }
    });
  };

  const handleRemoveBulkItem = (id: string) => {
    setBulkItems((prev) => prev.filter((item) => item.id !== id));
  };

  const handleSelectBulkResult = (itemId: string, result: OSMResult) => {
    setBulkItems((prev) =>
      prev.map((item) => {
        if (item.id === itemId) {
          return { ...item, selectedResult: result, status: "found" }; // Mark as found/confirmed
        }
        return item;
      }),
    );
  };

  const onSubmit = (data: RequestFormValues) => {
    startTransition(async () => {
      const result = await submitCityRequest(data, selectedLocation || {});

      if (result.error) {
        toast.error(result.error);
      } else {
        toast.success(
          "Demande envoyée ! Revenez bientôt pour voir le résultat.",
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
      <DialogContent className="w-screen h-screen max-w-none rounded-none border-0 sm:border sm:w-full sm:h-auto sm:max-w-lg sm:rounded-lg sm:max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Demander des villes</DialogTitle>
          <DialogDescription>
            Nous générons les villes à la demande.
          </DialogDescription>
        </DialogHeader>

        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="flex-1 flex flex-col overflow-hidden"
        >
          <TabsList className="grid w-full grid-cols-2 px-1">
            <TabsTrigger value="single">Recherche Unique</TabsTrigger>
            <TabsTrigger value="bulk">Import en masse</TabsTrigger>
          </TabsList>

          <TabsContent
            value="single"
            className="flex-1 overflow-y-auto py-4 px-1"
          >
            <div className="grid gap-4">
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

                    <DialogFooter>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
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
          </TabsContent>

          <TabsContent
            value="bulk"
            className="flex-1 flex flex-col gap-4 overflow-hidden py-4"
          >
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Collez une liste de villes (une par ligne) :
              </p>
              <Textarea
                placeholder={`Paris\nLyon\nMarseille\nBordeaux`}
                value={bulkInput}
                onChange={(e) => setBulkInput(e.target.value)}
                className="max-h-28 md:max-h-35"
                disabled={isAnalyzing || bulkItems.length > 0}
              />
              <div className="flex justify-end gap-2">
                {bulkItems.length > 0 && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      setBulkItems([]);
                      setBulkInput("");
                    }}
                  >
                    Réinitialiser
                  </Button>
                )}
                <Button
                  onClick={analyzeBulkInput}
                  disabled={
                    isAnalyzing || !bulkInput.trim() || bulkItems.length > 0
                  }
                  className={bulkItems.length > 0 ? "hidden" : ""}
                >
                  {isAnalyzing && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Analyser la liste
                </Button>
                {bulkItems.length > 0 && !isAnalyzing && (
                  <Button
                    onClick={submitBulkItems}
                    disabled={
                      isPending ||
                      bulkItems.filter(
                        (i) =>
                          (i.status === "found" || i.status === "ambiguous") &&
                          i.selectedResult,
                      ).length === 0
                    }
                  >
                    {isPending && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    Envoyer la sélection
                  </Button>
                )}
              </div>
            </div>

            {bulkItems.length > 0 && (
              <div className="flex-1 flex flex-col min-h-0 border rounded-md">
                <div className="p-2 border-b bg-muted/50 text-xs font-medium flex justify-between">
                  <span>
                    Résultats (
                    {
                      bulkItems.filter(
                        (i) =>
                          i.status === "found" ||
                          i.status === "ambiguous" ||
                          i.status === "submitted",
                      ).length
                    }
                    /{bulkItems.length})
                  </span>
                  {isAnalyzing && (
                    <span className="flex items-center gap-1">
                      <Loader2 className="h-3 w-3 animate-spin" /> Recherche en
                      cours...
                    </span>
                  )}
                </div>
                <div className="overflow-y-auto">
                  <div className="divide-y">
                    {bulkItems.map((item) => (
                      <div
                        key={item.id}
                        className="p-3 flex items-start gap-3 text-sm"
                      >
                        <div className="mt-0.5 shrink-0">
                          {item.status === "searching" && (
                            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                          )}
                          {(item.status === "found" ||
                            item.status === "submitted") && (
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                          )}
                          {item.status === "ambiguous" && (
                            <AlertCircle className="h-4 w-4 text-orange-500" />
                          )}
                          {(item.status === "not_found" ||
                            item.status === "error") && (
                            <XCircle className="h-4 w-4 text-destructive" />
                          )}
                        </div>

                        <div className="flex-1 space-y-1">
                          <div className="font-medium">
                            {item.originalQuery}
                          </div>

                          {item.error && (
                            <div className="text-destructive text-xs">
                              {item.error}
                            </div>
                          )}
                          {item.status === "not_found" && (
                            <div className="text-muted-foreground text-xs">
                              Aucun résultat trouvé
                            </div>
                          )}

                          {(item.status === "found" ||
                            item.status === "ambiguous" ||
                            item.status === "submitted") &&
                            item.results.length > 1 && (
                              <div className="flex gap-2">
                                {item.status === "submitted" ? (
                                  <div className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                                    Envoyé : {item.selectedResult?.display_name}
                                  </div>
                                ) : (
                                  <Select
                                    value={
                                      item.selectedResult?.place_id.toString() ??
                                      ""
                                    }
                                    onValueChange={(val) => {
                                      const res = item.results.find(
                                        (r) => r.place_id.toString() === val,
                                      );
                                      if (res)
                                        handleSelectBulkResult(item.id, res);
                                    }}
                                  >
                                    <SelectTrigger className="h-8 text-xs w-full max-w-50">
                                      <span className="truncate block text-left">
                                        {item.selectedResult ? (
                                          <>
                                            {item.selectedResult.address.city ||
                                              item.selectedResult.address
                                                .town ||
                                              item.selectedResult.address
                                                .village ||
                                              item.selectedResult.address
                                                .municipality ||
                                              item.selectedResult.display_name.split(
                                                ",",
                                              )[0]}
                                            {item.selectedResult.address
                                              .postcode &&
                                              ` (${item.selectedResult.address.postcode})`}
                                          </>
                                        ) : (
                                          <span className="text-muted-foreground">
                                            Choisir...
                                          </span>
                                        )}
                                      </span>
                                    </SelectTrigger>
                                    <SelectContent
                                      className="max-w-100 z-60"
                                      position="popper"
                                      side="bottom"
                                      align="start"
                                    >
                                      {item.results.map((r) => {
                                        const city =
                                          r.address.city ||
                                          r.address.town ||
                                          r.address.village ||
                                          r.address.municipality ||
                                          r.display_name.split(",")[0];
                                        const postcode = r.address.postcode;

                                        return (
                                          <SelectItem
                                            key={r.place_id}
                                            value={r.place_id.toString()}
                                            className="text-xs"
                                          >
                                            <div className="flex flex-col text-left gap-0.5 py-1">
                                              <span className="font-semibold text-sm">
                                                {city}
                                                {postcode && (
                                                  <span className="text-muted-foreground font-normal ml-1">
                                                    ({postcode})
                                                  </span>
                                                )}
                                              </span>
                                              <span className="text-[10px] text-muted-foreground wrap-break-word whitespace-normal leading-tight opacity-80">
                                                {r.display_name}
                                              </span>
                                            </div>
                                          </SelectItem>
                                        );
                                      })}
                                    </SelectContent>
                                  </Select>
                                )}
                              </div>
                            )}
                        </div>

                        {item.status !== "submitted" && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 shrink-0 text-muted-foreground hover:text-destructive"
                            onClick={() => handleRemoveBulkItem(item.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
