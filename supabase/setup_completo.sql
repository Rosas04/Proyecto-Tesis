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
-- ════════════════════════════════════════════════════════════════════════
-- FrontMind AI — Row Level Security, privilegios e índices
-- Aplicar en Supabase: SQL Editor → pegar y ejecutar (o `supabase db push`).
-- Es idempotente: puede ejecutarse más de una vez.
--
-- Tablas usadas por Front/src/historyService.js:
--   projects(id, user_id, project_name, source_type, ...)
--   analysis_runs(id, user_id, project_id, global_score, quality_level,
--                 total_findings, input_hash, created_at, ...)
--   analysis_findings(id, analysis_run_id, dimension, subdimension,
--                     severity, finding, recommendation, ...)
-- ════════════════════════════════════════════════════════════════════════

-- ── 1. Activar y forzar RLS ───────────────────────────────────────────────
alter table public.projects          enable row level security;
alter table public.analysis_runs     enable row level security;
alter table public.analysis_findings enable row level security;

alter table public.projects          force row level security;
alter table public.analysis_runs     force row level security;
alter table public.analysis_findings force row level security;

-- ── 2. Privilegios mínimos ────────────────────────────────────────────────
-- El rol anónimo (sin sesión) no necesita acceder a estas tablas.
revoke all on public.projects, public.analysis_runs, public.analysis_findings from anon;
-- Los usuarios autenticados sólo leen, crean y borran (no hay updates en la app).
revoke all on public.projects, public.analysis_runs, public.analysis_findings from authenticated;
grant select, insert, delete on public.projects, public.analysis_runs, public.analysis_findings to authenticated;

-- ── 3. Políticas: cada usuario sólo ve y modifica lo suyo ─────────────────
-- projects
drop policy if exists "projects_select_own" on public.projects;
drop policy if exists "projects_insert_own" on public.projects;
drop policy if exists "projects_delete_own" on public.projects;

create policy "projects_select_own" on public.projects
  for select to authenticated using (user_id = (select auth.uid()));
create policy "projects_insert_own" on public.projects
  for insert to authenticated with check (user_id = (select auth.uid()));
create policy "projects_delete_own" on public.projects
  for delete to authenticated using (user_id = (select auth.uid()));

-- analysis_runs (el project_id también debe pertenecer al usuario)
drop policy if exists "runs_select_own" on public.analysis_runs;
drop policy if exists "runs_insert_own" on public.analysis_runs;
drop policy if exists "runs_delete_own" on public.analysis_runs;

create policy "runs_select_own" on public.analysis_runs
  for select to authenticated using (user_id = (select auth.uid()));
create policy "runs_insert_own" on public.analysis_runs
  for insert to authenticated with check (
    user_id = (select auth.uid())
    and exists (
      select 1 from public.projects p
      where p.id = project_id and p.user_id = (select auth.uid())
    )
  );
create policy "runs_delete_own" on public.analysis_runs
  for delete to authenticated using (user_id = (select auth.uid()));

-- analysis_findings (propiedad heredada de la ejecución)
drop policy if exists "findings_select_own" on public.analysis_findings;
drop policy if exists "findings_insert_own" on public.analysis_findings;
drop policy if exists "findings_delete_own" on public.analysis_findings;

create policy "findings_select_own" on public.analysis_findings
  for select to authenticated using (
    exists (
      select 1 from public.analysis_runs r
      where r.id = analysis_run_id and r.user_id = (select auth.uid())
    )
  );
create policy "findings_insert_own" on public.analysis_findings
  for insert to authenticated with check (
    exists (
      select 1 from public.analysis_runs r
      where r.id = analysis_run_id and r.user_id = (select auth.uid())
    )
  );
create policy "findings_delete_own" on public.analysis_findings
  for delete to authenticated using (
    exists (
      select 1 from public.analysis_runs r
      where r.id = analysis_run_id and r.user_id = (select auth.uid())
    )
  );

-- ── 4. Índices para las consultas de la app y para las políticas RLS ──────
-- fetchUserRuns: where user_id = ? order by created_at desc
create index if not exists idx_analysis_runs_user_created
  on public.analysis_runs (user_id, created_at desc);
-- join projects(project_name) y política runs_insert_own
create index if not exists idx_analysis_runs_project
  on public.analysis_runs (project_id);
-- addAnalysisRun: where user_id = ? and project_name = ?
create index if not exists idx_projects_user_name
  on public.projects (user_id, project_name);
-- fetchRunFindings: where analysis_run_id = ? order by id
create index if not exists idx_analysis_findings_run
  on public.analysis_findings (analysis_run_id, id);

-- ── 5. Restricciones de integridad (si aún no existen) ────────────────────
do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'analysis_runs_score_range'
  ) then
    alter table public.analysis_runs
      add constraint analysis_runs_score_range
      check (global_score is null or (global_score >= 0 and global_score <= 100)) not valid;
  end if;
end $$;
