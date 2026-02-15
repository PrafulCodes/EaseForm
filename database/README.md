# EaseForm Database Architecture

## Overview

EaseForm uses **Supabase** as the backend, which provides:
- PostgreSQL database
- Supabase Auth for authentication
- Row Level Security (RLS) for data protection
- Real-time subscriptions

## Core Principles

### 🔐 Authentication Layer

**Supabase Auth is the single source of truth for user identity.**

- User credentials (email, password, OAuth) are stored in `auth.users` (managed by Supabase)
- **NEVER** store passwords in custom tables
- **NEVER** re-implement authentication logic
- Always use `auth.uid()` to get the current user's ID

### 👥 User Types

1. **Hosts (Form Creators)** - Authenticated users who create forms
2. **Respondents** - Anonymous users who fill out forms (NO authentication required)

## Database Schema

### 1. `public.hosts` Table

**Purpose:** Stores profile and usage data for form creators

```sql
create table public.hosts (
    id uuid primary key references auth.users(id) on delete cascade,
    name text not null,
    email text unique not null,
    active_forms_count integer default 0,
    created_at timestamp with time zone default now()
);
```

**Key Rules:**
- `id` matches `auth.users.id` (same UUID)
- One row per authenticated host
- Passwords are **NOT** stored here
- `active_forms_count` is a cached value, not source of truth

### 2. `public.forms` Table

**Purpose:** Stores forms created by hosts

```sql
create table public.forms (
    id uuid primary key default gen_random_uuid(),
    host_id uuid references public.hosts(id) on delete cascade,
    title text not null,
    description text,
    is_active boolean default true,
    one_response_per_device boolean default true,
    created_at timestamp with time zone default now()
);
```

**Key Rules:**
- Each form belongs to exactly one host
- Forms are linked via `host_id`
- **NEVER** store form lists inside the hosts table
- Use queries to get a host's forms, not embedded data

## Security Model (Row Level Security)

### RLS is ALWAYS Enabled

All tables have Row Level Security enabled to ensure:
- Hosts can only access their own data
- Data isolation between users
- Automatic enforcement at the database level

### Policy Logic

**For `hosts` table:**
```sql
auth.uid() = id
```

**For `forms` table:**
```sql
auth.uid() = host_id
```

### Frontend Requirements

All authenticated pages must:
1. Check for an active Supabase session
2. Redirect to `/auth/login.html` if no session exists
3. Use `auth.uid()` for ownership checks

## Application Rules

### ✅ DO

- Use Supabase client for all database operations
- Rely on `auth.uid()` for ownership
- Assume RLS is enforced
- Treat `hosts` as profile data, not auth data
- Check session state before accessing protected pages

### ❌ DON'T

- Store passwords in custom tables
- Bypass RLS policies
- Assume passwords are accessible
- Store form lists in the hosts table
- Allow respondents to authenticate

## Data Relationships

```
auth.users (Supabase managed)
    ↓
public.hosts (1:1 with auth.users)
    ↓
public.forms (1:many with hosts)
```

## Migration Files

See the `migrations/` directory for SQL scripts to set up the database schema and RLS policies.

## Code Generation Guidelines

When generating code for EaseForm:

1. **Authentication:** Always use Supabase Auth
2. **Queries:** Assume RLS is enforced
3. **Ownership:** Use `auth.uid()` for filtering
4. **Security:** Never bypass RLS
5. **Schema:** Follow the defined tables exactly

---

**This architecture is intentional and should not be altered unless explicitly requested.**
