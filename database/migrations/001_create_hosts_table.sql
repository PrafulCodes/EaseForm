-- ============================================
-- Migration: Create Hosts Table
-- Description: Stores profile data for form creators (hosts)
-- ============================================

-- Create the hosts table
create table public.hosts (
    id uuid primary key references auth.users(id) on delete cascade,
    name text not null,
    email text unique not null,
    active_forms_count integer default 0,
    created_at timestamp with time zone default now()
);

-- Enable Row Level Security
alter table public.hosts enable row level security;

-- Policy: Hosts can only read their own data
create policy "Hosts can view own profile"
    on public.hosts
    for select
    using (auth.uid() = id);

-- Policy: Hosts can update their own data
create policy "Hosts can update own profile"
    on public.hosts
    for update
    using (auth.uid() = id);

-- Policy: New hosts can insert their own profile (during signup)
create policy "Hosts can insert own profile"
    on public.hosts
    for insert
    with check (auth.uid() = id);

-- Policy: Hosts can delete their own profile
create policy "Hosts can delete own profile"
    on public.hosts
    for delete
    using (auth.uid() = id);

-- Create index for faster email lookups
create index hosts_email_idx on public.hosts(email);

-- Create index for faster lookups by id
create index hosts_id_idx on public.hosts(id);
