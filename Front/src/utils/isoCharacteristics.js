/**
 * Características ISO/IEC 25010:2023 que evalúa FrontMind.
 *
 * Núcleo: adecuación funcional, capacidad de interacción, compatibilidad,
 * flexibilidad, seguridad y fiabilidad. Eficiencia de desempeño es opcional.
 * Mantenibilidad no se evalúa (requiere el código fuente).
 *
 * Las claves antiguas se conservan sólo para mostrar análisis guardados antes
 * del cambio de modelo.
 */
export const CORE_CHARACTERISTICS = [
  "adecuacion_funcional",
  "capacidad_interaccion",
  "compatibilidad",
  "flexibilidad",
  "seguridad",
  "fiabilidad",
];

export const OPTIONAL_CHARACTERISTICS = ["eficiencia_desempeno"];

export const CHARACTERISTIC_LABELS = {
  adecuacion_funcional: "Adecuación funcional",
  capacidad_interaccion: "Capacidad de interacción",
  compatibilidad: "Compatibilidad",
  flexibilidad: "Flexibilidad",
  seguridad: "Seguridad",
  fiabilidad: "Fiabilidad",
  eficiencia_desempeno: "Eficiencia de desempeño",
  // Claves de análisis anteriores
  usabilidad: "Usabilidad",
  accesibilidad: "Accesibilidad",
  mantenibilidad: "Mantenibilidad",
  portabilidad: "Portabilidad",
};

export const SHORT_LABELS = {
  "Adecuación funcional": "Funcional",
  "Capacidad de interacción": "Interacción",
  "Compatibilidad": "Compatib.",
  "Flexibilidad": "Flexibil.",
  "Seguridad": "Seguridad",
  "Fiabilidad": "Fiabilidad",
  "Eficiencia de desempeño": "Eficiencia",
  "Usabilidad": "Usabilidad",
  "Accesibilidad": "Accesib.",
  "Mantenibilidad": "Mantenib.",
  "Portabilidad": "Portabil.",
};

export const characteristicLabel = (key) => CHARACTERISTIC_LABELS[key] || key;

/**
 * Filas a mostrar: las características evaluadas (con puntaje) seguidas de
 * las no evaluadas por falta de evidencia, en el orden del modelo.
 */
export function characteristicRows(scores = {}, notEvaluated = []) {
  const order = [...CORE_CHARACTERISTICS, ...OPTIONAL_CHARACTERISTICS];
  const keys = [
    ...order.filter((k) => typeof scores[k] === "number" || notEvaluated.includes(k)),
    ...Object.keys(scores).filter((k) => !order.includes(k)),
  ];
  return keys.map((key) => ({
    key,
    label: characteristicLabel(key),
    value: typeof scores[key] === "number" ? scores[key] : null,
  }));
}
