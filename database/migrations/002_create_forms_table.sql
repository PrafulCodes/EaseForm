-- ============================================
-- Migration: Create Forms Table
-- Description: Stores forms created by hosts
-- ============================================

-- Create the forms table
create table public.forms (
    id uuid primary key default gen_random_uuid(),
    host_id uuid not null references public.hosts(id) on delete cascade,
    title text not null,
    description text,
    is_active boolean default true,
    one_response_per_device boolean default true,
    created_at timestamp with time zone default now()
);

-- Enable Row Level Security
alter table public.forms enable row level security;

-- Policy: Hosts can only view their own forms
create policy "Hosts can view own forms"
    on public.forms
    for select
    using (auth.uid() = host_id);

-- Policy: Hosts can create forms (must be their own)
create policy "Hosts can create own forms"
    on public.forms
    for insert
    with check (auth.uid() = host_id);

-- Policy: Hosts can update their own forms
create policy "Hosts can update own forms"
    on public.forms
    for update
    using (auth.uid() = host_id);

-- Policy: Hosts can delete their own forms
create policy "Hosts can delete own forms"
    on public.forms
    for delete
    using (auth.uid() = host_id);

-- Policy: Allow public read access for active forms (for respondents)
-- Respondents need to view forms to fill them out
create policy "Public can view active forms"
    on public.forms
    for select
    using (is_active = true);

-- Create index for faster lookups by host_id
create index forms_host_id_idx on public.forms(host_id);

-- Create index for faster lookups by is_active
create index forms_is_active_idx on public.forms(is_active);

-- Create index for created_at for sorting
create index forms_created_at_idx on public.forms(created_at desc);
