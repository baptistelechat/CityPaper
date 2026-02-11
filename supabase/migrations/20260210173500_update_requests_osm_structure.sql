-- Update requests table structure to match OSM admin levels
-- Using separate columns for structured data querying, while keeping metadata for extra info

-- Add OSM-specific columns
alter table requests
add column if not exists country text,
add column if not exists state text, -- Region
add column if not exists county text, -- Departement
add column if not exists postcode text;

-- Add comment to clarify usage
comment on column requests.city is 'City/Village name (OSM admin_level 8)';
comment on column requests.state is 'State/Region (OSM admin_level 4)';
comment on column requests.county is 'County/Department (OSM admin_level 6)';
comment on column requests.country is 'Country name';

-- Update RLS policies to include new columns (implicit in INSERT/SELECT if not specifying columns)
-- But we might want to ensure they are covered if we had column-level security (we don't)
