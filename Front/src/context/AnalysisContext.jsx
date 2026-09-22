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
  const abortControllerRef = useRef(null);

  const cleanPreviousAnalysis = () => {
    localStorage.removeItem("inputType");
    localStorage.removeItem("inputUrl");
    localStorage.removeItem("inputZip");
    localStorage.removeItem("zipResult");
    storageService.clearAnalysisFlow();
  };

  const cancelAnalysis = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setLoading(false);
    setCurrentTaskName("");
    setError("El análisis fue cancelado por el usuario.");
  };

  const startAnalysis = async ({ activeTab, url, zipFile, zipName, useCredentials, credentials, maxPages }) => {
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

    try {
      setLoading(true);
      
      if (activeTab === "url") {
        const result = await captureInterfaceByUrl(url.trim(), credentials, maxPages, signal);
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

        localStorage.setItem("zipResult", JSON.stringify(result));
        localStorage.setItem("captureResult", JSON.stringify(captureResult));
        navigate("/capture");
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log("Análisis cancelado.");
        // We already set error in cancelAnalysis, so we do nothing here.
      } else {
        setError(err?.message || "Ocurrió un error. Verifique que el backend esté encendido.");
        console.error(err);
      }
    } finally {
      if (abortControllerRef.current && abortControllerRef.current.signal === signal) {
        setLoading(false);
        setCurrentTaskName("");
        abortControllerRef.current = null;
      }
    }
  };

  return (
    <AnalysisContext.Provider value={{ loading, currentTaskName, error, setError, startAnalysis, cancelAnalysis }}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  return useContext(AnalysisContext);
}
