/**
 * Centralized service to manage localStorage for the application flow
 */
class StorageService {
  constructor() {
    this.KEYS = {
      CAPTURE_RESULT: "captureResult",
      HTML_REPLICA_RESULT: "htmlReplicaResult",
      HTML_TO_EVALUATE: "htmlToEvaluate",
      ISO_EVALUATION: "isoEvaluation",
      TECHNICAL_REPORT: "technicalReport"
    };
  }

  // Generic getter/setter with error handling
  getItem(key) {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      console.error(`Error reading ${key} from localStorage:`, e);
      return null;
    }
  }

  setItem(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (e) {
      console.error(`Error saving ${key} to localStorage (possibly quota exceeded):`, e);
      // Removed global fallback to window here to enforce architecture
      return false;
    }
  }

  removeItem(key) {
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

  clearAnalysisFlow() {
    Object.values(this.KEYS).forEach(key => this.removeItem(key));
  }
}

export const storageService = new StorageService();
