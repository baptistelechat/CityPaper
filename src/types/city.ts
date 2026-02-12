export interface City {
  id: string;
  slug?: string;
  name: string;
  country: string;
  coordinates: string;
  status?: string;
  last_updated?: string;
  admin_info?: {
    structured?: {
      country?: string;
      state?: string;
      county?: string;
      city?: string;
      postcode?: string;
    };
  };
}
