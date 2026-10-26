-- ════════════════════════════════════════════════════════════════════════
-- FrontMind AI — Tablas base (ejecutar ANTES de 20261010000000_rls_e_indices.sql)
-- Supabase: SQL Editor → pegar y ejecutar. Es idempotente.
-- ════════════════════════════════════════════════════════════════════════

create table if not exists public.projects (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  project_name text not null,
  source_type  text not null default 'url',
  created_at   timestamptz not null default now()
);

create table if not exists public.analysis_runs (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users(id) on delete cascade,
  project_id     uuid not null references public.projects(id) on delete cascade,
  global_score   numeric,
  quality_level  text,
  total_findings integer not null default 0,
  input_hash     text,
  created_at     timestamptz not null default now()
);

create table if not exists public.analysis_findings (
  id              bigint generated always as identity primary key,
  analysis_run_id uuid not null references public.analysis_runs(id) on delete cascade,
  dimension       text,
  subdimension    text,
  severity        text,
  finding         text,
  recommendation  text,
  created_at      timestamptz not null default now()
);
