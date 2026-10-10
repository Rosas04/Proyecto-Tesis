/**
 * Escala única de nivel de calidad, idéntica a la del backend
 * (services/iso_service.get_level y agents/report_agent):
 *   90-100 Excelente · 80-89 Alto · 60-79 Medio · 40-59 Bajo · 0-39 Crítico
 */
export const QUALITY_LEVELS = [
  { min: 90, label: "Excelente", color: "#10b981", range: "90-100" },
  { min: 80, label: "Alto", color: "#3b82f6", range: "80-89" },
  { min: 60, label: "Medio", color: "#f59e0b", range: "60-79" },
  { min: 40, label: "Bajo", color: "#f97316", range: "40-59" },
  { min: 0, label: "Crítico", color: "#ef4444", range: "0-39" },
];

const UNKNOWN = { label: "N/D", color: "#94a3b8", range: "" };

/** Puntaje numérico válido o null (nunca se inventa un valor). */
export function toScore(value) {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export function getQualityLevel(score) {
  const s = toScore(score);
  if (s === null) return UNKNOWN;
  return QUALITY_LEVELS.find((level) => s >= level.min) || QUALITY_LEVELS[QUALITY_LEVELS.length - 1];
}
