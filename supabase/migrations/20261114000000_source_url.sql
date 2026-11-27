-- URL completa analizada (null en proyectos ZIP). Se muestra en el Historial.
alter table public.analysis_runs add column if not exists source_url text;
