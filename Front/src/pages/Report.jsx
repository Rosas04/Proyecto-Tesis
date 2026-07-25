import { useEffect, useMemo, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import Sidebar from "../components/Sidebar";
import { generateReport } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { addAnalysisRun } from "../historyService";
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
      } catch (err) {
        console.error(err);
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
    } catch (err) {
      setError("No se pudo leer la evaluación almacenada.");
      console.error(err);
    }
  }, []);

  const generateTechnicalReport = async (evaluation) => {
    try {
      setLoading(true);
      setError("");

      const userId = user?.id || null;
      const result = await generateReport(evaluation, userId);

      setReportResult(result);
      localStorage.setItem("technicalReport", JSON.stringify(result));

      // Guardar el análisis en la base de datos si el usuario está autenticado
      if (user && user.id) {
        try {
          const evalData = evaluation || {};
          const findings = evalData.findings || [];
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
          
          const savedHtml = localStorage.getItem("htmlToEvaluate") || "";
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
            } catch (e) {
              console.error("Error al extraer el dominio de la URL:", e);
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
          });
          console.log("Análisis guardado en historial de Supabase exitosamente.");
        } catch (dbErr) {
          console.error("Error al persistir el análisis en Supabase:", dbErr);
        }
      }
    } catch (err) {
      setError(
        "No se pudo generar el reporte técnico. Verifique que el backend esté encendido."
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const summary = useMemo(() => reportResult?.summary || {}, [reportResult]);
  const scores = useMemo(() => reportResult?.scores || {}, [reportResult]);
  const findings = useMemo(
    () => (Array.isArray(reportResult?.findings) ? reportResult.findings : []),
    [reportResult]
  );
  const recommendations = useMemo(
    () =>
      Array.isArray(reportResult?.main_recommendations)
        ? reportResult.main_recommendations
        : [],
    [reportResult]
  );

  const sourceLabel =
    inputType === "zip"
      ? inputZip || "Proyecto ZIP"
      : inputUrl || "No especificada";

  const scoreLabels = {
    adecuacion_funcional: "Adecuación funcional",
    eficiencia_desempeno: "Eficiencia de desempeño",
    usabilidad: "Usabilidad",
    accesibilidad: "Accesibilidad",
    mantenibilidad: "Mantenibilidad",
    compatibilidad: "Compatibilidad",
    seguridad: "Seguridad",
    portabilidad: "Portabilidad",
  };

  const getScoreClass = (score) => {
    if (score >= 90) return "excellent";
    if (score >= 80) return "high";
    if (score >= 60) return "medium";
    if (score >= 40) return "low";
    return "critical";
  };

  const goBack = () => {
    navigate("/evaluation");
  };

  const startNewAnalysis = () => {
    localStorage.removeItem("inputType");
    localStorage.removeItem("inputUrl");
    localStorage.removeItem("inputZip");
    localStorage.removeItem("captureResult");
    localStorage.removeItem("zipResult");
    localStorage.removeItem("htmlReplicaResult");
    localStorage.removeItem("htmlToEvaluate");
    localStorage.removeItem("isoEvaluation");
    localStorage.removeItem("technicalReport");
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
    } catch (err) {
      setError("No se pudo generar el archivo PDF del reporte.");
      console.error(err);
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
        <section className="page-header">
          <p className="page-kicker">Agente de Reporte</p>
          <h1 className="page-title">Reporte técnico final</h1>
          <p className="page-description">
            En esta etapa, el framework consolida los resultados de la
            evaluación ISO/IEC 25010 en un informe técnico profesional, listo
            para descarga y presentación.
          </p>
        </section>

        {error && <div className="error-box">{error}</div>}

        {loading && (
          <div className="loading-box">
            Generando reporte técnico consolidado. Espere unos segundos...
          </div>
        )}

        {!loading && reportResult && (
          <>
            <section className="report-hero card">
              <div className="score-circle-wrapper">
                <div
                  className={`score-circle ${getScoreClass(
                    summary.global_score ?? 0
                  )}`}
                >
                  <strong>{summary.global_score ?? 0}</strong>
                  <span>/100</span>
                </div>
              </div>

              <div className="report-hero-content">
                <span className="result-label">Nivel de calidad</span>
                <h2>{summary.quality_level || "No calculado"}</h2>
                <p>{reportResult.technical_conclusion}</p>
              </div>
            </section>

            <section className="report-summary card">
              <div>
                <span className="summary-label">Fuente evaluada</span>
                <strong>{sourceLabel}</strong>
              </div>

              <div>
                <span className="summary-label">Tipo de entrada</span>
                <strong>{inputType.toUpperCase()}</strong>
              </div>

              <div>
                <span className="summary-label">Generado el</span>
                <strong>{reportResult.generated_at || "No especificado"}</strong>
              </div>

              <div>
                <span className="summary-label">Total de hallazgos</span>
                <strong>{summary.total_findings ?? findings.length}</strong>
              </div>

              {summary.total_interfaces !== undefined && (
                <>
                  <div>
                    <span className="summary-label">Total de interfaces</span>
                    <strong>{summary.total_interfaces}</strong>
                  </div>
                  <div>
                    <span className="summary-label">Mejor interfaz</span>
                    <strong>{summary.best_interface || "N/A"}</strong>
                  </div>
                  <div>
                    <span className="summary-label">Peor interfaz</span>
                    <strong>{summary.worst_interface || "N/A"}</strong>
                  </div>
                </>
              )}
            </section>

            <section className="severity-grid">
              <article className="severity-card card critical">
                <span>Críticas</span>
                <strong>{summary.severity_summary?.["Crítica"] || 0}</strong>
              </article>

              <article className="severity-card card high">
                <span>Altas</span>
                <strong>{summary.severity_summary?.Alta || 0}</strong>
              </article>

              <article className="severity-card card medium">
                <span>Medias</span>
                <strong>{summary.severity_summary?.Media || 0}</strong>
              </article>

              <article className="severity-card card low">
                <span>Bajas</span>
                <strong>{summary.severity_summary?.Baja || 0}</strong>
              </article>
            </section>

            <section className="scores-section card">
              <div className="section-header">
                <h2>Puntajes finales por dimensión</h2>
                <p>
                  Resultados consolidados de la evaluación técnica ISO/IEC
                  25010 aplicada al artefacto frontend.
                </p>
              </div>

              <div className="score-list">
                {Object.entries(scoreLabels).map(([key, label]) => (
                  <div className="score-row" key={key}>
                    <div className="score-row-label">
                      <strong>{label}</strong>
                      <span>{scores[key] ?? 0}/100</span>
                    </div>

                    <div className="score-bar">
                      <div
                        className={`score-bar-fill ${getScoreClass(
                          scores[key] ?? 0
                        )}`}
                        style={{ width: `${scores[key] ?? 0}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {recommendations.length > 0 && (
              <section className="recommendations-section card">
                <div className="section-header">
                  <h2>Recomendaciones principales</h2>
                  <p>
                    Listado priorizado de mejoras técnicas a implementar en el
                    frontend evaluado.
                  </p>
                </div>

                <ul>
                  {recommendations.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </section>
            )}

            <section className="findings-section card">
              <div className="section-header">
                <h2>Detalle de hallazgos técnicos</h2>
                <p>
                  Hallazgos clasificados por dimensión y severidad según
                  ISO/IEC 25010.
                </p>
              </div>

              {findings.length > 0 ? (
                <div className="findings-table-wrapper">
                  <table className="findings-table">
                    <thead>
                      <tr>
                        <th>N°</th>
                        <th>Dimensión</th>
                        <th>Severidad</th>
                        <th>Hallazgo</th>
                        <th>Recomendación</th>
                      </tr>
                    </thead>

                    <tbody>
                      {findings.map((item, index) => (
                        <tr key={index}>
                          <td>{index + 1}</td>
                          <td>{item.dimension || "No especificada"}</td>
                          <td>{item.severity || "Media"}</td>
                          <td>
                            {item.finding?.includes('[VIOLACIÓN]') ? (
                              <>
                                <span className="badge">VIOLACIÓN</span>
                                {item.finding.replace('[VIOLACIÓN]', '')}
                              </>
                            ) : (
                              item.finding || "Hallazgo no especificado."
                            )}
                          </td>
                          <td>
                            {item.recommendation ||
                              "No se registró recomendación."}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="success-box">
                  No se detectaron hallazgos técnicos relevantes.
                </div>
              )}
            </section>

            <div className="page-actions">
              <button className="secondary-btn" type="button" onClick={goBack}>
                Volver
              </button>

              <button
                className="secondary-btn"
                type="button"
                onClick={startNewAnalysis}
              >
                Nuevo análisis
              </button>

              <button
                className="primary-btn"
                type="button"
                onClick={downloadPdf}
                disabled={generatingPdf}
              >
                {generatingPdf ? "Generando PDF..." : "Descargar reporte PDF"}
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}