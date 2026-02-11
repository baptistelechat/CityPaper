-- Create requests table
create table requests (
  id uuid primary key default gen_random_uuid(),
  city text not null,
  email text,
  status text default 'pending',
  metadata jsonb default '{}'::jsonb,
  created_at timestamp with time zone default now()
);

-- Enable RLS
alter table requests enable row level security;

-- Policy: Allow public inserts (anon and authenticated)
create policy "Enable insert for everyone"
on requests
for insert
to anon, authenticated
with check (true);

-- Policy: Restrict select/update to service_role only (implicit deny for others)
-- No policy needed for select/update for anon as default is deny.
-- Service role bypasses RLS automatically.

create policy "Enable select for service role only"
on requests
for select
to service_role
using (true);
