import { supabase } from './lib/supabase.js';

/**
 * Agrega un nuevo análisis de auditoría técnica a Supabase.
 * Guarda el registro principal en `analysis_runs` y sus hallazgos asociados en `analysis_findings`.
 */
export async function addAnalysisRun({ 
  userId, 
  globalScore, 
  qualityLevel, 
  totalFindings, 
  findings,
  sourceType = 'url',
  inputHash = null,
  projectName = null
}) {
  if (!supabase) {
    throw new Error("Base de datos (Supabase) no configurada.");
  }
  if (!userId) {
    throw new Error("El ID del usuario es requerido para guardar en el historial.");
  }

  const finalInputHash = inputHash || `hash_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  const finalProjectName = projectName || (sourceType === 'zip' ? 'Proyecto ZIP' : 'Proyecto URL');

  // 1. Buscar si el usuario ya tiene un proyecto creado con este nombre
  let projectId;
  try {
    const { data: existingProjects, error: fetchProjError } = await supabase
      .from('projects')
      .select('id')
      .eq('user_id', userId)
      .eq('project_name', finalProjectName)
      .limit(1);

    if (fetchProjError) {
      console.error("Error al consultar proyectos del usuario:", fetchProjError);
      throw fetchProjError;
    }

    if (existingProjects && existingProjects.length > 0) {
      projectId = existingProjects[0].id;
    } else {
      // Crear un proyecto con el nombre indicado
      const { data: newProj, error: createProjError } = await supabase
        .from('projects')
        .insert([
          {
            user_id: userId,
            project_name: finalProjectName,
            source_type: sourceType
          }
        ])
        .select('id')
        .single();

      if (createProjError) {
        console.error("Error al crear proyecto:", createProjError);
        throw createProjError;
      }
      projectId = newProj.id;
    }
  } catch (projErr) {
    console.error("Fallo al resolver project_id:", projErr);
    throw new Error("No se pudo asociar o crear el proyecto para este análisis. Verifique políticas de la tabla 'projects'.");
  }

  // 2. Insertar el registro principal en `analysis_runs` vinculándolo a project_id
  const { data, error } = await supabase
    .from('analysis_runs')
    .insert([
      {
        user_id: userId,
        project_id: projectId,
        global_score: globalScore,
        quality_level: qualityLevel,
        total_findings: totalFindings,
        input_hash: finalInputHash
      }
    ])
    .select('id')
    .single();

  if (error) {
    console.error("Error al insertar en analysis_runs:", error);
    throw error;
  }

  const runId = data.id;

  // 2. Insertar los hallazgos en `analysis_findings` (si existen)
  if (findings && findings.length > 0) {
    const findingsData = findings.map(f => ({
      analysis_run_id: runId,
      dimension: f.dimension || "No especificada",
      subdimension: f.subdimension || "No especificada",
      severity: f.severity || "Media",
      finding: f.finding || "Hallazgo no especificado",
      recommendation: f.recommendation || "No se registró recomendación"
    }));

    const { error: findingsError } = await supabase
      .from('analysis_findings')
      .insert(findingsData);

    if (findingsError) {
      console.error("Error al insertar hallazgos en analysis_findings:", findingsError);
      throw findingsError;
    }
  }

  return runId;
}

export async function fetchUserRuns(userId) {
  if (!supabase) return [];
  if (!userId) return [];

  const { data, error } = await supabase
    .from('analysis_runs')
    .select('*, projects(project_name)')
    .eq('user_id', userId)
    .order('created_at', { ascending: false });

  if (error) {
    console.error("Error al recuperar analysis_runs:", error);
    throw error;
  }

  return data;
}

/**
 * Obtiene todos los hallazgos asociados a una ejecución específica.
 */
export async function fetchRunFindings(runId) {
  if (!supabase) return [];
  if (!runId) return [];

  const { data, error } = await supabase
    .from('analysis_findings')
    .select('*')
    .eq('analysis_run_id', runId)
    .order('id', { ascending: true });

  if (error) {
    console.error("Error al recuperar analysis_findings:", error);
    throw error;
  }

  return data;
}

