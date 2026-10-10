import { createContext, useContext, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { captureInterfaceByUrl, uploadZip } from "../services/api";
import { storageService } from "../services/storageService";

const AnalysisContext = createContext(null);

export function AnalysisProvider({ children }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentTaskName, setCurrentTaskName] = useState("");
  // Identificador de la tarea de captura: aísla el progreso entre usuarios
  const [currentJobId, setCurrentJobId] = useState(null);
  const abortControllerRef = useRef(null);

  const cleanPreviousAnalysis = () => {
    storageService.clearAll();
  };

  const cancelAnalysis = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setLoading(false);
    setCurrentTaskName("");
    setCurrentJobId(null);
    setError("El análisis fue cancelado por el usuario.");
  };

  const startAnalysis = async ({ activeTab, url, zipFile, zipName, credentials, maxPages }) => {
    setError("");
    
    if (activeTab === "url" && !url.trim()) {
      setError("Ingrese una URL válida para iniciar la captura.");
      return;
    }

    if (activeTab === "zip" && !zipFile) {
      setError("Seleccione un archivo ZIP del proyecto frontend.");
      return;
    }

    cleanPreviousAnalysis();
    localStorage.setItem("inputType", activeTab);
    localStorage.setItem("inputUrl", url.trim());
    localStorage.setItem("inputZip", zipName);
    
    setCurrentTaskName(activeTab === "url" ? url.trim() : zipName);

    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;
    const jobId = crypto.randomUUID();
    setCurrentJobId(jobId);

    try {
      setLoading(true);
      
      if (activeTab === "url") {
        const result = await captureInterfaceByUrl(url.trim(), credentials, maxPages, signal, jobId);

        if (result?.status === "error") {
          setError(result?.message || "No se pudo capturar la URL indicada.");
          return;
        }

        storageService.setCaptureResult(result);
        navigate("/capture");
      } else if (activeTab === "zip") {
        const result = await uploadZip(zipFile, signal);
        
        if (result?.status === "error" || result?.extraction?.status === "error") {
          setError(result?.extraction?.message || result?.message || "No se pudo procesar el archivo ZIP.");
          return;
        }

        const combinedHtml = result?.extraction?.combined_html || result?.html_content || result?.extraction?.combined_code || "";
        const interfaces = result?.extraction?.interfaces || [];
        const captures = result?.captures || [];

        const captureResult = {
          agent: "ZipInput",
          status: "completed",
          source_type: "zip",
          url: zipName,
          message: result?.extraction?.message || "Proyecto ZIP procesado correctamente.",
          html_content: combinedHtml,
          captures,
          total_captures: captures.length,
          interfaces,
          project_type: result?.extraction?.project_type || "unknown",
          zip_result: result,
        };

        storageService.setZipResult(result);
        storageService.setCaptureResult(captureResult);
        navigate("/capture");
      }
    } catch (err) {
      // AbortError: el mensaje ya lo puso cancelAnalysis
      if (err.name !== "AbortError") {
        setError(err?.message || "Ocurrió un error. Verifique que el backend esté encendido.");
      }
    } finally {
      if (abortControllerRef.current && abortControllerRef.current.signal === signal) {
        setLoading(false);
        setCurrentTaskName("");
        setCurrentJobId(null);
        abortControllerRef.current = null;
      }
    }
  };

  return (
    <AnalysisContext.Provider value={{ loading, currentTaskName, currentJobId, error, setError, startAnalysis, cancelAnalysis }}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  return useContext(AnalysisContext);
}
