-- Add updated_at column and remove email column
alter table requests
add column if not exists updated_at timestamp with time zone default now();

-- Drop email column as we stopped collecting/using it
alter table requests
drop column if exists email;
