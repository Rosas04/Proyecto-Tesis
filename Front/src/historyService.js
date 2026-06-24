import { supabase } from './lib/supabase.js';

export async function fetchHistory({ page = 1, pageSize = 20, analysisType = null }) {
  const from = (page - 1) * pageSize;
  const to = from + pageSize - 1;
  let query = supabase
    .from('analysis_history')
    .select('*')
    .order('created_at', { ascending: false })
    .range(from, to);
  if (analysisType) {
    query = query.eq('analysis_type', analysisType);
  }
  const { data, error } = await query;
  if (error) throw error;
  return data;
}

export async function addHistory(entry) {
  const { error } = await supabase.from('analysis_history').insert([entry]);
  if (error) throw error;
}
