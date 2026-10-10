/**
 * Centralized service to manage localStorage for the application flow.
 *
 * Los resultados de captura (HTML + CSS de varias interfaces) pueden superar
 * la cuota de localStorage (~5 MB). En ese caso el dato se conserva en memoria
 * durante la sesión de la pestaña para que el flujo no quede vacío.
 */
class StorageService {
  constructor() {
    this.KEYS = {
      CAPTURE_RESULT: "captureResult",
      HTML_REPLICA_RESULT: "htmlReplicaResult",
      HTML_TO_EVALUATE: "htmlToEvaluate",
      ISO_EVALUATION: "isoEvaluation",
      TECHNICAL_REPORT: "technicalReport",
      ZIP_RESULT: "zipResult",
    };
    this.memory = new Map();
  }

  // Generic getter/setter with error handling
  getItem(key) {
    if (this.memory.has(key)) return this.memory.get(key);
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      console.error(`Error reading ${key} from localStorage:`, e);
      return null;
    }
  }

  /**
   * Guarda el valor. Devuelve "local" si se persistió en localStorage,
   * "memory" si sólo pudo guardarse en memoria (cuota excedida).
   */
  setItem(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      this.memory.delete(key);
      return "local";
    } catch (e) {
      console.warn(`${key} excede la cuota de localStorage; se conserva en memoria.`, e);
      try {
        localStorage.removeItem(key);
      } catch {
        // localStorage no disponible
      }
      this.memory.set(key, value);
      return "memory";
    }
  }

  removeItem(key) {
    this.memory.delete(key);
    try {
      localStorage.removeItem(key);
    } catch (e) {
      console.error(`Error removing ${key}:`, e);
    }
  }

  // Specific helpers
  getCaptureResult() { return this.getItem(this.KEYS.CAPTURE_RESULT); }
  setCaptureResult(data) { return this.setItem(this.KEYS.CAPTURE_RESULT, data); }

  getHtmlReplicaResult() { return this.getItem(this.KEYS.HTML_REPLICA_RESULT); }
  setHtmlReplicaResult(data) { return this.setItem(this.KEYS.HTML_REPLICA_RESULT, data); }

  getHtmlToEvaluate() { return this.getItem(this.KEYS.HTML_TO_EVALUATE); }
  setHtmlToEvaluate(data) { return this.setItem(this.KEYS.HTML_TO_EVALUATE, data); }

  getIsoEvaluation() { return this.getItem(this.KEYS.ISO_EVALUATION); }
  setIsoEvaluation(data) { return this.setItem(this.KEYS.ISO_EVALUATION, data); }

  getTechnicalReport() { return this.getItem(this.KEYS.TECHNICAL_REPORT); }
  setTechnicalReport(data) { return this.setItem(this.KEYS.TECHNICAL_REPORT, data); }

  getZipResult() { return this.getItem(this.KEYS.ZIP_RESULT); }
  setZipResult(data) { return this.setItem(this.KEYS.ZIP_RESULT, data); }

  clearAnalysisFlow() {
    Object.values(this.KEYS).forEach(key => this.removeItem(key));
  }

  /** Borra todo el estado del análisis (se usa al cerrar sesión). */
  clearAll() {
    this.clearAnalysisFlow();
    ["inputType", "inputUrl", "inputZip"].forEach(key => this.removeItem(key));
    this.memory.clear();
  }
}

export const storageService = new StorageService();
