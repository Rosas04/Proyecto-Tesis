import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";
import Sidebar from "../components/Sidebar";
import { generateReport } from "../services/api";
import { storageService } from "../services/storageService";
import ReportView from "../components/ReportView";
import { useAuth } from "../context/AuthContext";
import { addAnalysisRun } from "../services/historyService";
import html2canvas from "html2canvas";
import { ReportDashboard } from "../components/ReportDashboard";
import "./Report.css";

export default function Report() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [reportResult, setReportResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [generatingPdf, setGeneratingPdf] = useState(false);
  
  const hasCalled = useRef(false);
  const dashboardRef = useRef(null);

  const inputUrl = localStorage.getItem("inputUrl") || "";
  const inputZip = localStorage.getItem("inputZip") || "";
  const inputType = localStorage.getItem("inputType") || "url";

  useEffect(() => {
    const savedReport = localStorage.getItem("technicalReport");
    const savedEvaluations = localStorage.getItem("isoEvaluations");
    const savedEvaluation = localStorage.getItem("isoEvaluation");

    if (savedReport) {
      try {
        setReportResult(JSON.parse(savedReport));
        return;
      } catch {
        // Reporte guardado corrupto: se regenera a partir de la evaluación
      }
    }

    if (!savedEvaluation && !savedEvaluations) {
      setError(
        "No se encontró una evaluación previa. Regrese a la etapa de evaluación ISO/IEC 25010."
      );
      return;
    }

    if (hasCalled.current) return;
    hasCalled.current = true;

    try {
      let evaluationData;
      if (savedEvaluations) {
          const parsedEvaluations = JSON.parse(savedEvaluations);
          // Assuming it's an array or an object values of array
          evaluationData = Array.isArray(parsedEvaluations) ? parsedEvaluations : Object.values(parsedEvaluations);
      } else {
          const parsedEvaluation = JSON.parse(savedEvaluation);
          evaluationData = parsedEvaluation?.evaluation || parsedEvaluation;
      }
      generateTechnicalReport(evaluationData);
    } catch {
      setError("No se pudo leer la evaluación almacenada.");
      
    }
  }, []);

  const generateTechnicalReport = async (evaluation) => {
    try {
      setLoading(true);
      setError("");

      const result = await generateReport(evaluation);
      const captured = storageService.getCaptureResult()?.interfaces?.length;
      if (result && captured) result.captured_interfaces = captured;

      setReportResult(result);
      localStorage.setItem("technicalReport", JSON.stringify(result));

      // Guardar el análisis en la base de datos si el usuario está autenticado
      if (user && user.id) {
        try {
          // Los hallazgos consolidados vienen en el reporte; la evaluación puede
          // ser una lista de interfaces sin campo `findings` propio.
          const evalData = evaluation || {};
          const findings = Array.isArray(result?.findings)
            ? result.findings
            : (Array.isArray(evalData.findings) ? evalData.findings : []);
          const localSourceType = localStorage.getItem("inputType") || "url";
          
          // Generar hash simple del HTML evaluado para identificar esta ejecución
          const generateSimpleHash = (str) => {
            let hash = 0;
            if (!str) return hash.toString();
            for (let i = 0; i < str.length; i++) {
              hash = (hash << 5) - hash + str.charCodeAt(i);
              hash |= 0;
            }
            return Math.abs(hash).toString(16);
          };
          
          const savedHtml = storageService.getHtmlToEvaluate() || "";
          const localInputHash = savedHtml ? generateSimpleHash(savedHtml) : `hash_${Date.now()}`;

          // Calcular el nombre del proyecto real basado en la URL o archivo ZIP
          const localInputUrl = localStorage.getItem("inputUrl") || "";
          const localInputZip = localStorage.getItem("inputZip") || "";
          let localProjectName = "Proyecto URL";

          if (localSourceType === "zip") {
            localProjectName = localInputZip || "Proyecto ZIP";
          } else if (localInputUrl) {
            try {
              let formattedUrl = localInputUrl.trim();
              if (!/^https?:\/\//i.test(formattedUrl)) {
                formattedUrl = "http://" + formattedUrl;
              }
              const urlObj = new URL(formattedUrl);
              let hostname = urlObj.hostname;
              if (hostname.startsWith("www.")) {
                hostname = hostname.substring(4);
              }
              localProjectName = hostname || localInputUrl;
            } catch {
              localProjectName = localInputUrl;
            }
          }

          await addAnalysisRun({
            userId: user.id,
            globalScore: result.summary?.global_score ?? 0,
            qualityLevel: result.summary?.quality_level || "No calculado",
            totalFindings: result.summary?.total_findings ?? findings.length,
            findings: findings,
            sourceType: localSourceType,
            inputHash: localInputHash,
            projectName: localProjectName,
            sourceUrl: localSourceType === "zip" ? null : localInputUrl || null,
            scores: result?.scores || null,
          });
        } catch (dbErr) {
          console.error("No se pudo guardar el análisis en el historial:", dbErr);
          setError("El reporte se generó, pero no se pudo guardar en el historial.");
        }
      }
    } catch {
      setError(
        "No se pudo generar el reporte técnico. Verifique que el backend esté encendido."
      );
      
    } finally {
      setLoading(false);
    }
  };

  const sourceLabel =
    inputType === "zip"
      ? inputZip || "Proyecto ZIP"
      : inputUrl || "No especificada";

  const goBack = () => {
    navigate("/evaluation");
  };

  const startNewAnalysis = () => {
    storageService.clearAll();
    navigate("/input");
  };

  const downloadPdf = async () => {
    if (!reportResult) {
      return;
    }

    try {
      setGeneratingPdf(true);

      const doc = new jsPDF({ unit: "pt", format: "a4", orientation: "portrait" });
      const pages = dashboardRef.current?.querySelectorAll('.pdf-page');

      if (!pages || pages.length === 0) {
        throw new Error("No se encontraron las páginas del reporte para capturar.");
      }

      for (let i = 0; i < pages.length; i++) {
        const pageElement = pages[i];
        
        // Use html2canvas to capture the DOM node
        const canvas = await html2canvas(pageElement, {
          scale: 2, // higher resolution
          useCORS: true,
          logging: false,
          backgroundColor: '#ffffff'
        });

        const imgData = canvas.toDataURL("image/jpeg", 1.0);
        
        const pdfWidth = doc.internal.pageSize.getWidth();
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
        
        if (i > 0) {
          doc.addPage();
        }
        
        doc.addImage(imgData, "JPEG", 0, 0, pdfWidth, pdfHeight);
      }

      const fileSafeSource = sourceLabel
        .replace(/^https?:\/\//, "")
        .replace(/[^a-zA-Z0-9]/g, "_")
        .slice(0, 40);

      doc.save(`reporte-frontmind-${fileSafeSource || "evaluacion"}.pdf`);
    } catch {
      setError("No se pudo generar el archivo PDF del reporte.");
      
    } finally {
      setGeneratingPdf(false);
    }
  };


  return (
    <div className="layout">
      <Sidebar />

      <main className="report-main">
        {reportResult && (
          <ReportDashboard 
            ref={dashboardRef} 
            reportResult={reportResult} 
            sourceLabel={sourceLabel} 
            inputType={inputType} 
          />
        )}
        
        {error && <div className="error-box">{error}</div>}
        {loading && <div className="loading-box">Generando reporte técnico consolidado. Espere unos segundos...</div>}

        {!loading && reportResult && (
          <ReportView
            reportResult={reportResult}
            sourceLabel={sourceLabel}
            inputType={inputType}
            onDownload={downloadPdf}
            generatingPdf={generatingPdf}
            onBack={goBack}
            onNew={startNewAnalysis}
          />
        )}

        {!loading && !reportResult && !error && (
          <div className="loading-box">Preparando el informe...</div>
        )}
      </main>
    </div>
  );
}