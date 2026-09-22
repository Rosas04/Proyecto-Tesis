import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";
import { useAnalysis } from "../context/AnalysisContext";
import { fetchUserRuns, fetchRunFindings } from "../historyService";
import html2canvas from "html2canvas";
import { ReportDashboard } from "../components/ReportDashboard";
import "./History.css";

// --- ICONS ---
const RefreshIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 4 23 10 17 10"></polyline>
    <polyline points="1 20 1 14 7 14"></polyline>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
  </svg>
);
const SortIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="7 15 12 20 17 15"></polyline>
    <polyline points="7 9 12 4 17 9"></polyline>
  </svg>
);
const LinkIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
  </svg>
);
const DocIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
  </svg>
);
const EyeIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
);
const MoreIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="1"></circle>
    <circle cx="19" cy="12" r="1"></circle>
    <circle cx="5" cy="12" r="1"></circle>
  </svg>
);
const CheckCircleIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);
const CrossCircleIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

export default function History() {
  const { user, loadingAuth } = useAuth();
  const { loading: analysisLoading, currentTaskName, cancelAnalysis } = useAnalysis();
  const navigate = useNavigate();
  
  const [runs, setRuns] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [error, setError] = useState("");
  const [generatingPdfId, setGeneratingPdfId] = useState(null);
  
  // Detalle del análisis seleccionado
  const [selectedRun, setSelectedRun] = useState(null);
  const [findings, setFindings] = useState([]);
  const [loadingFindings, setLoadingFindings] = useState(false);

  // PDF Dashboard ref and data
  const dashboardRef = React.useRef(null);
  const [downloadData, setDownloadData] = useState(null);

  // Filtros y paginación
  const [filterScore, setFilterScore] = useState("");
  const [filterQuality, setFilterQuality] = useState("");
  const [filterDate, setFilterDate] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const filteredRuns = useMemo(() => {
    return runs.filter((run) => {
      if (filterQuality && filterQuality !== "Todos" && run.quality_level !== filterQuality) {
        return false;
      }
      if (filterScore) {
        const scoreLimit = parseInt(filterScore, 10);
        if (!isNaN(scoreLimit) && run.global_score < scoreLimit) {
          return false;
        }
      }
      if (filterDate) {
        const runDateStr = new Date(run.created_at).toISOString().split("T")[0];
        if (runDateStr !== filterDate) {
          return false;
        }
      }
      return true;
    });
  }, [runs, filterQuality, filterScore, filterDate]);

  const paginatedRuns = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredRuns.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredRuns, currentPage, itemsPerPage]);

  const totalPages = Math.max(1, Math.ceil(filteredRuns.length / itemsPerPage));

  useEffect(() => {
    setCurrentPage(1);
  }, [filterQuality, filterScore, filterDate]);

  useEffect(() => {
    if (loadingAuth) return;
    if (!user) {
      setError("Inicie sesión para visualizar su historial de análisis.");
      return;
    }
    loadHistory();
  }, [user, loadingAuth]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") setSelectedRun(null);
    };
    if (selectedRun) window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedRun]);

  const loadHistory = async () => {
    try {
      setLoadingHistory(true);
      setError("");
      const data = await fetchUserRuns(user.id);
      setRuns(data);
    } catch (err) {
      console.error(err);
      setError("No se pudo cargar el historial de análisis.");
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSelectRun = async (run) => {
    setSelectedRun(run);
    setFindings([]);
    try {
      setLoadingFindings(true);
      const data = await fetchRunFindings(run.id);
      setFindings(data);
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar los hallazgos de este análisis.");
    } finally {
      setLoadingFindings(false);
    }
  };

  const handleDownloadReport = async (run, e) => {
    e.stopPropagation();
    try {
      setGeneratingPdfId(run.id);
      const runFindings = await fetchRunFindings(run.id);
      const projectName = run.projects?.project_name || "Proyecto Principal";
      const severitySummary = { "Crítica": 0, "Alta": 0, "Media": 0, "Baja": 0 };
      const recommendations = [];
      runFindings.forEach(f => {
         const sev = f.severity || 'Media';
         if(severitySummary[sev] !== undefined) severitySummary[sev]++;
         if(f.recommendation && f.recommendation !== "Sin recomendación registrada.") {
           if(!recommendations.includes(f.recommendation)) {
              recommendations.push(f.recommendation);
           }
         }
      });
      const mockReportResult = {
        generated_at: new Date(run.created_at).toLocaleString("es-ES"),
        summary: {
          global_score: run.global_score,
          quality_level: run.quality_level,
          total_findings: run.total_findings,
          total_interfaces: 1,
          severity_summary: severitySummary
        },
        scores: {},
        findings: runFindings,
        main_recommendations: recommendations
      };
      setDownloadData({ reportResult: mockReportResult, sourceLabel: projectName });
    } catch (err) {
      console.error(err);
      setError("No se pudo preparar el reporte para descarga.");
      setGeneratingPdfId(null);
    }
  };

  useEffect(() => {
    const processPdf = async () => {
      if (downloadData && dashboardRef.current) {
        try {
          const doc = new jsPDF({ unit: "pt", format: "a4", orientation: "portrait" });
          const pages = dashboardRef.current.querySelectorAll('.pdf-page');
          for (let i = 0; i < pages.length; i++) {
            const pageElement = pages[i];
            const canvas = await html2canvas(pageElement, { scale: 2, useCORS: true, logging: false });
            const imgData = canvas.toDataURL("image/jpeg", 1.0);
            const pdfWidth = doc.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
            if (i > 0) doc.addPage();
            doc.addImage(imgData, "JPEG", 0, 0, pdfWidth, pdfHeight);
          }
          const fileSafeSource = downloadData.sourceLabel.replace(/^https?:\/\//, "").replace(/[^a-zA-Z0-9]/g, "_").slice(0, 40);
          doc.save(`Reporte_${fileSafeSource || "Historial"}.pdf`);
        } catch (err) {
          console.error(err);
          setError("No se pudo generar el reporte PDF.");
        } finally {
          setGeneratingPdfId(null);
          setDownloadData(null);
        }
      }
    };
    processPdf();
  }, [downloadData]);

  const getScoreStyle = (score) => {
    if (score === 0) return "none";
    if (score >= 90) return "excellent";
    if (score >= 80) return "high";
    if (score >= 60) return "medium";
    if (score >= 40) return "low";
    return "critical";
  };

  const getQualityPillStyle = (level) => {
    if (level === "Excelente") return "excellent";
    if (level === "Alto") return "high";
    if (level === "No calculado") return "none";
    return "none";
  };

  const getSeverityClass = (severity) => {
    if (severity === "Crítica") return "critical";
    if (severity === "Alta") return "high";
    if (severity === "Media") return "medium";
    return "low";
  };

  const formatDateTime = (dateString) => {
    const d = new Date(dateString);
    return (
      <>
        <div>{d.toLocaleDateString("es-ES")}</div>
        <div>{d.toLocaleTimeString("es-ES")}</div>
      </>
    );
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="history-main">
        {downloadData && (
          <ReportDashboard 
            ref={dashboardRef} 
            reportResult={downloadData.reportResult} 
            sourceLabel={downloadData.sourceLabel} 
            inputType="url"
          />
        )}
        
        <header className="history-header">
          <div className="history-title-group">
            <h1>Historial de análisis y calidad</h1>
            <p>Consulta los resultados de tus evaluaciones realizadas. Puedes filtrar por criterios y acceder al detalle de cada análisis.</p>
          </div>
          <button 
            className="new-analysis-btn" 
            onClick={() => {
              if (analysisLoading) cancelAnalysis();
              localStorage.removeItem("zipResult");
              localStorage.removeItem("captureResult");
              localStorage.removeItem("htmlReplicaResult");
              localStorage.removeItem("htmlToEvaluate");
              navigate("/input");
            }}
          >
            + Nuevo análisis
          </button>
        </header>

        {error && <div className="error-box">{error}</div>}

        {loadingAuth || loadingHistory ? (
          <div className="loading-box">Cargando historial de análisis...</div>
        ) : !user ? (
          <div className="error-box">Inicie sesión para acceder a esta sección.</div>
        ) : (
          <div className="history-content">
            
            {/* Filters */}
            <div className="filters-card">
              <div className="filters-group-wrapper">
                <div className="filter-item">
                  <label htmlFor="filterScore">Puntaje mínimo</label>
                  <div className="filter-input-wrapper">
                    <input
                      id="filterScore"
                      type="number"
                      placeholder="Ej. 80"
                      value={filterScore}
                      onChange={(e) => setFilterScore(e.target.value)}
                    />
                    <SortIcon className="filter-icon-right" />
                  </div>
                </div>

                <div className="filter-item">
                  <label htmlFor="filterQuality">Nivel de calidad</label>
                  <div className="filter-input-wrapper">
                    <select
                      id="filterQuality"
                      value={filterQuality}
                      onChange={(e) => setFilterQuality(e.target.value)}
                    >
                      <option value="Todos">Todos</option>
                      <option value="Excelente">Excelente</option>
                      <option value="Alto">Alto</option>
                      <option value="Medio">Medio</option>
                      <option value="Bajo">Bajo</option>
                      <option value="Crítico">Crítico</option>
                      <option value="No calculado">No calculado</option>
                    </select>
                    <SortIcon className="filter-icon-right" />
                  </div>
                </div>

                <div className="filter-item">
                  <label htmlFor="filterDate">Fecha de análisis</label>
                  <div className="filter-input-wrapper">
                    <input
                      id="filterDate"
                      type="date"
                      value={filterDate}
                      onChange={(e) => setFilterDate(e.target.value)}
                    />
                  </div>
                </div>
              </div>
              <button
                className="clear-btn"
                onClick={() => { setFilterScore(""); setFilterQuality("Todos"); setFilterDate(""); }}
              >
                <RefreshIcon /> Limpiar filtros
              </button>
            </div>

            {/* Table */}
            <div className="table-card">
              <div className="table-wrapper">
                <table className="runs-table">
                  <thead>
                    <tr>
                      <th style={{ width: "40px", paddingRight: 0 }}>
                        <input type="checkbox" className="custom-checkbox" disabled />
                      </th>
                      <th>Proyecto / URL</th>
                      <th>Fecha y hora <SortIcon /></th>
                      <th>Puntaje global <SortIcon /></th>
                      <th>Nivel de calidad <SortIcon /></th>
                      <th>Hallazgos <SortIcon /></th>
                      <th>Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedRuns.map((run) => {
                      const scoreStyle = getScoreStyle(run.global_score);
                      const qualityStyle = getQualityPillStyle(run.quality_level);
                      const displayScore = run.global_score;
                      
                      return (
                        <tr key={run.id}>
                          <td style={{ width: "40px", paddingRight: 0 }}>
                            <input type="checkbox" className="custom-checkbox" />
                          </td>
                          <td className="project-name-cell">
                            <strong>{run.projects?.project_name || "Proyecto Principal"}</strong>
                            <a href="#" className="url-link" onClick={e => e.preventDefault()}>
                              <LinkIcon /> {run.url || "https://example.com"}
                            </a>
                          </td>
                          <td className="date-cell">
                            {formatDateTime(run.created_at)}
                          </td>
                          <td>
                            <div className="score-cell">
                              <div className={`score-icon ${scoreStyle}`}>
                                {scoreStyle === "none" || scoreStyle === "critical" ? <CrossCircleIcon /> : <CheckCircleIcon />}
                              </div>
                              {displayScore}/100
                            </div>
                          </td>
                          <td>
                            <span className={`quality-pill ${qualityStyle}`}>
                              {run.quality_level || "No calculado"}
                            </span>
                          </td>
                          <td>
                            <div className="findings-cell">
                              <DocIcon /> {run.total_findings} hallazgos
                            </div>
                          </td>
                          <td>
                            <div className="action-cell">
                              <button className="btn-details" onClick={() => handleSelectRun(run)}>
                                <EyeIcon /> Ver detalles
                              </button>
                              <button className="btn-more" onClick={(e) => handleDownloadReport(run, e)} title="Descargar PDF">
                                <MoreIcon />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="pagination-wrapper">
                <div className="pagination-text">
                  Mostrando {paginatedRuns.length} de {filteredRuns.length} resultados
                </div>
                <div className="pagination-controls">
                  <button 
                    className="page-btn" 
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  >
                    {"<"}
                  </button>
                  <button className="page-btn active">{currentPage}</button>
                  <button 
                    className="page-btn" 
                    disabled={currentPage === totalPages || totalPages === 0}
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  >
                    {">"}
                  </button>
                </div>
              </div>
            </div>

            {/* Modal de Detalles */}
            {selectedRun && (
              <div className="modal-overlay" onClick={() => setSelectedRun(null)}>
                <section className="modal-container" onClick={(e) => e.stopPropagation()}>
                  <div className="details-header">
                    <div>
                      <h2>Detalles del Análisis</h2>
                      <p className="details-subtitle">
                        Ejecutado el {new Date(selectedRun.created_at).toLocaleString("es-ES")}
                      </p>
                    </div>
                    <button className="close-details-btn" onClick={() => setSelectedRun(null)}>
                      Cerrar detalles
                    </button>
                  </div>
                  
                  <div style={{display: 'flex', gap: '20px', marginBottom: '24px'}}>
                    <div style={{flex: 1, padding: '20px', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0'}}>
                      <div style={{fontSize: '12px', color: '#64748b', fontWeight: 700}}>PUNTAJE GLOBAL</div>
                      <div style={{fontSize: '24px', fontWeight: 800, marginTop: '8px'}}>{selectedRun.global_score}</div>
                    </div>
                    <div style={{flex: 1, padding: '20px', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0'}}>
                      <div style={{fontSize: '12px', color: '#64748b', fontWeight: 700}}>NIVEL DE CALIDAD</div>
                      <div style={{fontSize: '24px', fontWeight: 800, marginTop: '8px'}}>{selectedRun.quality_level}</div>
                    </div>
                    <div style={{flex: 1, padding: '20px', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0'}}>
                      <div style={{fontSize: '12px', color: '#64748b', fontWeight: 700}}>HALLAZGOS TOTALES</div>
                      <div style={{fontSize: '24px', fontWeight: 800, marginTop: '8px'}}>{selectedRun.total_findings}</div>
                    </div>
                  </div>

                  {loadingFindings ? (
                    <div style={{padding: '40px', textAlign: 'center'}}>Cargando hallazgos...</div>
                  ) : (
                    <div className="findings-table-wrapper">
                      <table className="findings-table">
                        <thead>
                          <tr>
                            <th>N°</th>
                            <th>Dimensión</th>
                            <th>Subdimensión</th>
                            <th>Severidad</th>
                            <th>Hallazgo</th>
                            <th>Recomendación</th>
                          </tr>
                        </thead>
                        <tbody>
                          {findings.map((item, index) => (
                            <tr key={item.id || index}>
                              <td>{index + 1}</td>
                              <td>{item.dimension}</td>
                              <td>{item.subdimension}</td>
                              <td>
                                <span className={`severity-pill ${getSeverityClass(item.severity)}`}>
                                  {item.severity}
                                </span>
                              </td>
                              <td>{item.finding}</td>
                              <td>{item.recommendation}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </section>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
