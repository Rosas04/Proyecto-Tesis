/**
 * Características ISO/IEC 25010:2023 que muestra FrontMind.
 *
 * Centrales: las observables en la interfaz renderizada; son las únicas que
 * ponderan en la nota global (selección según ISO/IEC 25040).
 * Complementarias: se miden y se informan, pero no entran en la nota.
 */
export const CORE_CHARACTERISTICS = [
  { key: "adecuacion_funcional", label: "Adecuación funcional", short: "Funcional" },
  { key: "usabilidad", label: "Capacidad de interacción", short: "Interacción" },
  { key: "compatibilidad", label: "Compatibilidad", short: "Compatib." },
  { key: "portabilidad", label: "Flexibilidad", short: "Flexibil." },
];

export const COMPLEMENTARY_CHARACTERISTICS = [
  { key: "accesibilidad", label: "Inclusividad (WCAG 2.2)", short: "WCAG" },
  { key: "eficiencia_desempeno", label: "Eficiencia de desempeño", short: "Desempeño" },
  { key: "mantenibilidad", label: "Mantenibilidad", short: "Mantenib." },
  { key: "seguridad", label: "Seguridad", short: "Seguridad" },
];

function valueOf(result, key) {
  const v = result?.scores?.[key] ?? result?.complementary_scores?.[key];
  return typeof v === "number" ? v : null;
}

/** Puntajes de un resultado de evaluación o reporte, separados en centrales y complementarios. */
export function characteristicScores(result) {
  const map = (items) => items.map((c) => ({ ...c, value: valueOf(result, c.key) }));
  return {
    core: map(CORE_CHARACTERISTICS),
    complementary: map(COMPLEMENTARY_CHARACTERISTICS).filter((c) => c.value !== null),
  };
}
