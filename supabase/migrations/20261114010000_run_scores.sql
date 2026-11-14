-- Puntajes por característica ISO/IEC 25010 del análisis (para el PDF del Historial).
alter table public.analysis_runs add column if not exists scores jsonb;
