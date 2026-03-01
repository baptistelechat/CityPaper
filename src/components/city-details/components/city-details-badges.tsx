import { City } from "@/types/city";
import { Badge } from "@/components/ui/badge";

export const CityDetailsBadges = ({ city }: { city: City }) => {
  const data = city.admin_info?.structured;

  if (!data) {
    return <></>;
  }

  return (
    <div className="flex flex-wrap gap-2 mt-4">
      {data?.state && <Badge variant="outline">{data.state}</Badge>}
      {data?.county && <Badge variant="outline">{data.county}</Badge>}
    </div>
  );
};
