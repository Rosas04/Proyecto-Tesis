/**
 * Escala única de nivel de calidad, idéntica a la del backend
 * (services/iso_service.get_level y agents/report_agent):
 *   90-100 Excelente · 80-89 Alto · 60-79 Medio · 40-59 Bajo · 0-39 Crítico
 */
export const QUALITY_LEVELS = [
  { min: 90, label: "Excelente", color: "#047857", range: "90-100" },
  { min: 80, label: "Alto", color: "#2563eb", range: "80-89" },
  { min: 60, label: "Medio", color: "#b45309", range: "60-79" },
  { min: 40, label: "Bajo", color: "#c2410c", range: "40-59" },
  { min: 0, label: "Crítico", color: "#b91c1c", range: "0-39" },
];

const UNKNOWN = { label: "N/D", color: "#5f6d82", range: "" };

/** Puntaje numérico válido o null (nunca se inventa un valor). */
export function toScore(value) {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export function getQualityLevel(score) {
  const s = toScore(score);
  if (s === null) return UNKNOWN;
  return QUALITY_LEVELS.find((level) => s >= level.min) || QUALITY_LEVELS[QUALITY_LEVELS.length - 1];
}
