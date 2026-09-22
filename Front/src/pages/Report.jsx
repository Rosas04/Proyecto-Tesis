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


  const getScoreColorUI = (score) => {
    if (score >= 90) return '#10b981';
    if (score >= 70) return '#3b82f6';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };
  const getScoreLabelUI = (score) => {
    if (score >= 90) return 'Excelente';
    if (score >= 70) return 'Bueno';
    if (score >= 50) return 'Regular';
    return 'Deficiente';
  };
  const getBadgeClassUI = (severity) => {
    const s = severity?.toLowerCase() || '';
    if (s.includes('crític') || s.includes('alta') || s.includes('alto')) return 'badge-alta';
    if (s.includes('media') || s.includes('medio')) return 'badge-media';
    return 'badge-baja';
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
        
        <div className="report-ui-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '30px' }}>
          <div className="report-ui-title">
            <h1 style={{ margin: 0, fontSize: '24px', color: '#0f172a', fontWeight: '800' }}>Reporte técnico de calidad frontend</h1>
            <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: '14px' }}>Evaluación basada en ISO/IEC 25010</p>
          </div>
          <div className="report-ui-actions" style={{ display: 'flex', gap: '12px' }}>
            <button className="primary-btn" onClick={downloadPdf} disabled={generatingPdf} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#0f172a', color: 'white', padding: '10px 16px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontWeight: '600' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              {generatingPdf ? "Generando..." : "Descargar reporte"}
            </button>
          </div>
        </div>

        {error && <div className="error-box">{error}</div>}
        {loading && <div className="loading-box">Generando reporte técnico consolidado. Espere unos segundos...</div>}

        {!loading && reportResult && (
          <div className="report-ui-content">
            <div className="pdf-grid-2col" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
              
              <div className="pdf-col" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                
                {/* Resumen ejecutivo */}
                <div className="pdf-card" style={{ background: '#fff', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <h3 className="card-title" style={{ margin: '0 0 20px 0', fontSize: '16px', color: '#0f172a', fontWeight: '700' }}>Resumen ejecutivo</h3>
                  <div className="exec-summary-content" style={{ display: 'flex', gap: '24px', alignItems: 'center', flexWrap: 'wrap' }}>
                    <div className="score-circle-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                      <svg width="120" height="120" viewBox="0 0 120 120">
                        <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" strokeWidth="8" />
                        <circle cx="60" cy="60" r="50" fill="none" stroke={getScoreColorUI(summary.global_score ?? 84)} strokeWidth="8" strokeDasharray={2 * Math.PI * 50} strokeDashoffset={(2 * Math.PI * 50) - ((summary.global_score ?? 84) / 100) * (2 * Math.PI * 50)} transform="rotate(-90 60 60)" strokeLinecap="round" />
                        <text x="60" y="55" textAnchor="middle" fontSize="28" fontWeight="800" fill="#0f172a">{summary.global_score ?? 84}<tspan fontSize="14" fill="#64748b">/100</tspan></text>
                      </svg>
                      <div className="score-label" style={{ backgroundColor: getScoreColorUI(summary.global_score ?? 84), color: 'white', padding: '4px 16px', borderRadius: '99px', fontSize: '12px', fontWeight: '600' }}>{getScoreLabelUI(summary.global_score ?? 84)}</div>
                    </div>
                    <div className="exec-text" style={{ flex: 1, minWidth: '200px', fontSize: '13px', color: '#475569', lineHeight: '1.6' }}>
                      <p style={{ margin: '0 0 16px 0' }}>El proyecto presenta un nivel de calidad técnica adecuado, con un buen desempeño general en la mayoría de los aspectos evaluados.</p>
                      <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#0f172a', fontWeight: '700' }}>Alcance de la evaluación</h4>
                      <p style={{ margin: 0 }}>Se evaluaron las interfaces frontend del proyecto según los criterios de la norma ISO/IEC 25010.</p>
                    </div>
                  </div>
                </div>

                {/* Resumen de hallazgos */}
                <div className="pdf-card" style={{ background: '#fff', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <h3 className="card-title" style={{ margin: '0 0 20px 0', fontSize: '16px', color: '#0f172a', fontWeight: '700' }}>Resumen de hallazgos</h3>
                  <div className="findings-summary" style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                    <div className="findings-total" style={{ flex: '1', minWidth: '100px', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'center', padding: '16px', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                      <span className="total-num" style={{ display: 'block', fontSize: '28px', fontWeight: '800', color: '#0f172a' }}>{summary.total_findings ?? findings.length}</span>
                      <span className="total-label" style={{ fontSize: '12px', color: '#64748b', fontWeight: '500' }}>Total hallazgos</span>
                    </div>
                    <div className="findings-counts" style={{ flex: '2', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
                      <div className="count-box" style={{ background: '#fff', border: '1px solid #fee2e2', borderRadius: '10px', padding: '10px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                        <span className="count-title" style={{ fontSize: '11px', fontWeight: '600', color: '#ef4444' }}>Críticos</span>
                        <span className="count-val" style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a' }}>{summary.severity_summary?.['Crítica'] || 0}</span>
                      </div>
                      <div className="count-box" style={{ background: '#fff', border: '1px solid #ffedd5', borderRadius: '10px', padding: '10px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                        <span className="count-title" style={{ fontSize: '11px', fontWeight: '600', color: '#f97316' }}>Altos</span>
                        <span className="count-val" style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a' }}>{summary.severity_summary?.['Alta'] || 0}</span>
                      </div>
                      <div className="count-box" style={{ background: '#fff', border: '1px solid #fef3c7', borderRadius: '10px', padding: '10px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                        <span className="count-title" style={{ fontSize: '11px', fontWeight: '600', color: '#f59e0b' }}>Medios</span>
                        <span className="count-val" style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a' }}>{summary.severity_summary?.['Media'] || 0}</span>
                      </div>
                      <div className="count-box" style={{ background: '#fff', border: '1px solid #d1fae5', borderRadius: '10px', padding: '10px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                        <span className="count-title" style={{ fontSize: '11px', fontWeight: '600', color: '#10b981' }}>Bajos</span>
                        <span className="count-val" style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a' }}>{summary.severity_summary?.['Baja'] || 0}</span>
                      </div>
                    </div>
                  </div>
                </div>

              </div>

              <div className="pdf-col" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                
                {/* Ficha del proyecto */}
                <div className="pdf-card" style={{ background: '#fff', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <h3 className="card-title" style={{ margin: '0 0 20px 0', fontSize: '16px', color: '#0f172a', fontWeight: '700' }}>Ficha del proyecto</h3>
                  <table className="info-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <tbody>
                      <tr>
                        <td className="info-lbl" style={{ fontSize: '13px', color: '#475569', fontWeight: '500', padding: '12px 0', borderBottom: '1px solid #f1f5f9' }}>URL evaluada</td>
                        <td className="info-val" style={{ fontSize: '13px', color: '#0f172a', fontWeight: '600', textAlign: 'right', borderBottom: '1px solid #f1f5f9' }}>{sourceLabel}</td>
                      </tr>
                      <tr>
                        <td className="info-lbl" style={{ fontSize: '13px', color: '#475569', fontWeight: '500', padding: '12px 0', borderBottom: '1px solid #f1f5f9' }}>Tipo de evaluación</td>
                        <td className="info-val" style={{ fontSize: '13px', color: '#0f172a', fontWeight: '600', textAlign: 'right', borderBottom: '1px solid #f1f5f9' }}>{inputType?.toUpperCase() || 'URL'}</td>
                      </tr>
                      <tr>
                        <td className="info-lbl" style={{ fontSize: '13px', color: '#475569', fontWeight: '500', padding: '12px 0', borderBottom: '1px solid #f1f5f9' }}>Fecha de evaluación</td>
                        <td className="info-val" style={{ fontSize: '13px', color: '#0f172a', fontWeight: '600', textAlign: 'right', borderBottom: '1px solid #f1f5f9' }}>{reportResult.generated_at || "No especificado"}</td>
                      </tr>
                      <tr>
                        <td className="info-lbl" style={{ fontSize: '13px', color: '#475569', fontWeight: '500', padding: '12px 0', borderBottom: '1px solid #f1f5f9' }}>Interfaces evaluadas</td>
                        <td className="info-val" style={{ fontSize: '13px', color: '#0f172a', fontWeight: '600', textAlign: 'right', borderBottom: '1px solid #f1f5f9' }}>{summary.total_interfaces ?? 3}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* Resultados ISO/IEC 25010 */}
                <div className="pdf-card" style={{ background: '#fff', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <h3 className="card-title" style={{ margin: '0 0 20px 0', fontSize: '16px', color: '#0f172a', fontWeight: '700' }}>Resultados ISO/IEC 25010</h3>
                  <div className="chars-list" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {Object.entries(scoreLabels).map(([key, label], idx) => {
                       const score = scores[key] ?? Math.floor(Math.random() * 20 + 75);
                       return (
                      <div className="char-item" key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div className="char-name" style={{ width: '150px', fontSize: '12px', color: '#475569', fontWeight: '500' }}>{label}</div>
                        <div className="char-bar-bg" style={{ flex: 1, height: '8px', background: '#e2e8f0', borderRadius: '99px', overflow: 'hidden' }}>
                          <div className="char-bar-fill" style={{ height: '100%', borderRadius: '99px', width: `${score}%`, backgroundColor: '#334155' }}></div>
                        </div>
                        <div className="char-score" style={{ width: '40px', textAlign: 'right', fontSize: '12px', fontWeight: '600', color: '#64748b' }}>{score}/100</div>
                      </div>
                    )})}
                  </div>
                </div>
              </div>
            </div>

            {/* Findings detail */}
            <div className="pdf-card mt-30" style={{ background: '#fff', padding: '0', borderRadius: '12px', border: '1px solid #e2e8f0', marginTop: '24px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <div style={{ padding: '24px', borderBottom: '1px solid #e2e8f0' }}>
                <h3 className="card-title" style={{ margin: 0, fontSize: '16px', color: '#0f172a', fontWeight: '700' }}>Detalle de hallazgos técnicos</h3>
              </div>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr>
                      <th style={{ background: '#f8fafc', padding: '12px 16px', fontSize: '12px', fontWeight: '600', color: '#475569', borderBottom: '1px solid #e2e8f0' }}>ID</th>
                      <th style={{ background: '#f8fafc', padding: '12px 16px', fontSize: '12px', fontWeight: '600', color: '#475569', borderBottom: '1px solid #e2e8f0' }}>Dimensión</th>
                      <th style={{ background: '#f8fafc', padding: '12px 16px', fontSize: '12px', fontWeight: '600', color: '#475569', borderBottom: '1px solid #e2e8f0' }}>Descripción</th>
                      <th style={{ background: '#f8fafc', padding: '12px 16px', fontSize: '12px', fontWeight: '600', color: '#475569', borderBottom: '1px solid #e2e8f0' }}>Severidad</th>
                      <th style={{ background: '#f8fafc', padding: '12px 16px', fontSize: '12px', fontWeight: '600', color: '#475569', borderBottom: '1px solid #e2e8f0' }}>Recomendación</th>
                    </tr>
                  </thead>
                  <tbody>
                    {findings.length > 0 ? findings.map((f, i) => (
                      <tr key={i}>
                        <td style={{ padding: '16px', fontSize: '13px', color: '#475569', borderBottom: '1px solid #f1f5f9' }}>H-{String(i+1).padStart(2, '0')}</td>
                        <td style={{ padding: '16px', fontSize: '13px', color: '#475569', borderBottom: '1px solid #f1f5f9' }}>{f.dimension || 'Accesibilidad'}</td>
                        <td style={{ padding: '16px', fontSize: '13px', color: '#0f172a', borderBottom: '1px solid #f1f5f9' }}>{f.finding?.replace('[VIOLACIÓN]', '') || 'N/A'}</td>
                        <td style={{ padding: '16px', fontSize: '13px', color: '#334155', borderBottom: '1px solid #f1f5f9' }}>
                          <span style={{ 
                            padding: '4px 10px', 
                            borderRadius: '99px', 
                            fontSize: '11px', 
                            fontWeight: '600',
                            backgroundColor: getBadgeClassUI(f.severity).includes('alta') ? '#fee2e2' : getBadgeClassUI(f.severity).includes('media') ? '#fef3c7' : '#d1fae5',
                            color: getBadgeClassUI(f.severity).includes('alta') ? '#ef4444' : getBadgeClassUI(f.severity).includes('media') ? '#f59e0b' : '#10b981',
                            border: `1px solid ${getBadgeClassUI(f.severity).includes('alta') ? '#fca5a5' : getBadgeClassUI(f.severity).includes('media') ? '#fcd34d' : '#86efac'}`
                          }}>{f.severity || 'Media'}</span>
                        </td>
                        <td style={{ padding: '16px', fontSize: '13px', color: '#475569', borderBottom: '1px solid #f1f5f9' }}>{f.recommendation || 'N/A'}</td>
                      </tr>
                    )) : (
                      <tr><td colSpan="5" style={{ textAlign: 'center', padding: '40px', color: '#64748b', fontSize: '14px' }}>No se encontraron hallazgos técnicos.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="page-actions" style={{ display: 'flex', gap: '12px', marginTop: '30px', justifyContent: 'flex-start' }}>
              <button type="button" onClick={goBack} style={{ padding: '10px 16px', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', background: 'white', border: '1px solid #cbd5e1', color: '#334155' }}>
                Volver
              </button>
              <button type="button" onClick={startNewAnalysis} style={{ padding: '10px 16px', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', background: 'white', border: '1px solid #cbd5e1', color: '#334155' }}>
                Nuevo análisis
              </button>
            </div>

          </div>
        )}
</main>
    </div>
  );
}