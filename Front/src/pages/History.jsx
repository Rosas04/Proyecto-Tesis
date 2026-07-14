import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";
import { fetchUserRuns, fetchRunFindings } from "../historyService";
import "./History.css";

export default function History() {
  const { user, loadingAuth } = useAuth();
  const navigate = useNavigate();
  
  const [runs, setRuns] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [error, setError] = useState("");
  const [generatingPdfId, setGeneratingPdfId] = useState(null);
  
  // Detalle del análisis seleccionado
  const [selectedRun, setSelectedRun] = useState(null);
  const [findings, setFindings] = useState([]);
  const [loadingFindings, setLoadingFindings] = useState(false);

  // Filtros y paginación
  const [filterScore, setFilterScore] = useState("");
  const [filterQuality, setFilterQuality] = useState("");
  const [filterDate, setFilterDate] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const filteredRuns = useMemo(() => {
    return runs.filter((run) => {
      // 1. Filtrar por nivel de calidad
      if (filterQuality && run.quality_level !== filterQuality) {
        return false;
      }

      // 2. Filtrar por porcentaje mínimo
      if (filterScore) {
        const scoreLimit = parseInt(filterScore, 10);
        if (!isNaN(scoreLimit) && run.global_score < scoreLimit) {
          return false;
        }
      }

      // 3. Filtrar por fecha
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

  // Resetear página a 1 cuando cambian los filtros
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

  // Cerrar modal con la tecla Escape
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        setSelectedRun(null);
      }
    };
    if (selectedRun) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
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
      
      const doc = new jsPDF({ unit: "pt", format: "a4" });
      const pageWidth = doc.internal.pageSize.getWidth();
      const marginX = 40;
      let cursorY = 50;

      doc.setFillColor(37, 99, 235);
      doc.rect(0, 0, pageWidth, 70, "F");

      doc.setTextColor(255, 255, 255);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(18);
      doc.text("FrontMind AI - Reporte técnico de evaluación frontend", marginX, 35);

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.text("Norma aplicada: ISO/IEC 25010", marginX, 52);

      cursorY = 95;
      doc.setTextColor(17, 24, 39);

      doc.setFont("helvetica", "bold");
      doc.setFontSize(12);
      doc.text("Información general", marginX, cursorY);
      cursorY += 18;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);

      const projectName = run.projects?.project_name || "Proyecto Principal";

      const generalInfo = [
        ["Proyecto", projectName],
        ["Fecha de análisis", new Date(run.created_at).toLocaleString("es-ES")],
        ["Puntaje global", `${run.global_score} / 100`],
        ["Nivel de calidad", run.quality_level],
        ["Total de hallazgos", `${run.total_findings}`],
      ];

      generalInfo.forEach(([label, value]) => {
        doc.setFont("helvetica", "bold");
        doc.text(`${label}:`, marginX, cursorY);
        doc.setFont("helvetica", "normal");
        doc.text(String(value), marginX + 150, cursorY);
        cursorY += 16;
      });

      if (runFindings.length > 0) {
        cursorY += 16;
        if (cursorY > 750) {
          doc.addPage();
          cursorY = 50;
        }

        doc.setFont("helvetica", "bold");
        doc.setFontSize(12);
        doc.text("Hallazgos técnicos detectados", marginX, cursorY);
        cursorY += 12;

        const findingsRows = runFindings.map((item, index) => [
          String(index + 1),
          item.dimension || "No especificada",
          item.severity || "Media",
          item.finding?.replace(/\[.*?\]\s*/g, '') || "Hallazgo no especificado.",
          item.recommendation || "Sin recomendación registrada.",
        ]);

        autoTable(doc, {
          startY: cursorY + 8,
          margin: { left: marginX, right: marginX },
          head: [["N°", "Dimensión", "Severidad", "Hallazgo", "Recomendación"]],
          body: findingsRows,
          theme: "striped",
          headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: "bold" },
          styles: { fontSize: 8, cellPadding: 5 },
          columnStyles: {
            0: { cellWidth: 22 },
            1: { cellWidth: 75 },
            2: { cellWidth: 55 },
            3: { cellWidth: 160 },
            4: { cellWidth: 160 },
          },
        });
      }

      // Nombre del archivo como solicitó el usuario
      const projectNameFile = projectName.replace(/https?:\/\//i, '').replace(/[\/\\]/g, '');
      doc.save(`Reporte_${projectNameFile}.pdf`);
    } catch (err) {
      console.error(err);
      setError("No se pudo generar el reporte PDF.");
    } finally {
      setGeneratingPdfId(null);
    }
  };

  const getScoreClass = (score) => {
    if (score >= 90) return "excellent";
    if (score >= 80) return "high";
    if (score >= 60) return "medium";
    if (score >= 40) return "low";
    return "critical";
  };

  const getSeverityClass = (severity) => {
    if (severity === "Crítica") return "critical";
    if (severity === "Alta") return "high";
    if (severity === "Media") return "medium";
    return "low";
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="history-main">
        <section className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ flex: '1 1 500px' }}>
            <p className="page-kicker">Historial de Auditoría</p>
            <h1 className="page-title">Historial de análisis y calidad</h1>
            <p className="page-description">
              Revise los diagnósticos técnicos frontend realizados en esta cuenta bajo la norma ISO/IEC 25010. 
              Haga clic en cualquier auditoría para ver el desglose de hallazgos detectados.
            </p>
          </div>
          <button 
            className="primary-btn" 
            style={{ width: 'auto', marginTop: '16px' }}
            onClick={() => {
              localStorage.removeItem("zipResult");
              localStorage.removeItem("captureResult");
              localStorage.removeItem("htmlReplicaResult");
              localStorage.removeItem("htmlToEvaluate");
              navigate("/input");
            }}
          >
            + Nuevo Análisis
          </button>
        </section>

        {error && <div className="error-box">{error}</div>}

        {loadingAuth || loadingHistory ? (
          <div className="loading-box">Cargando historial de análisis...</div>
        ) : !user ? (
          <div className="error-box">Inicie sesión para acceder a esta sección.</div>
        ) : (
          <div className="history-content">
            {/* Listado de Ejecuciones */}
            <section className="runs-section card">
              <h2>Análisis Realizados</h2>

              {/* Filtros de Búsqueda */}
              {runs.length > 0 && (
                <div className="filters-bar">
                  <div className="filter-group">
                    <label htmlFor="filterScore">Puntaje Mínimo</label>
                    <input
                      id="filterScore"
                      type="number"
                      min="0"
                      max="100"
                      placeholder="Ej. 80"
                      value={filterScore}
                      onChange={(e) => setFilterScore(e.target.value)}
                    />
                  </div>

                  <div className="filter-group">
                    <label htmlFor="filterQuality">Nivel de Calidad</label>
                    <select
                      id="filterQuality"
                      value={filterQuality}
                      onChange={(e) => setFilterQuality(e.target.value)}
                    >
                      <option value="">Todos</option>
                      <option value="Excelente">Excelente</option>
                      <option value="Alto">Alto</option>
                      <option value="Medio">Medio</option>
                      <option value="Bajo">Bajo</option>
                      <option value="Crítico">Crítico</option>
                    </select>
                  </div>

                  <div className="filter-group">
                    <label htmlFor="filterDate">Fecha de Análisis</label>
                    <input
                      id="filterDate"
                      type="date"
                      value={filterDate}
                      onChange={(e) => setFilterDate(e.target.value)}
                    />
                  </div>

                  {(filterScore || filterQuality || filterDate) && (
                    <button
                      className="clear-filters-btn"
                      onClick={() => {
                        setFilterScore("");
                        setFilterQuality("");
                        setFilterDate("");
                      }}
                    >
                      Limpiar filtros
                    </button>
                  )}
                </div>
              )}

              {runs.length === 0 ? (
                <div className="empty-box">
                  No se han registrado análisis en esta cuenta todavía.
                </div>
              ) : filteredRuns.length === 0 ? (
                <div className="empty-box">
                  No se encontraron análisis que coincidan con los filtros aplicados.
                </div>
              ) : (
                <>
                  <div className="table-wrapper">
                    <table className="runs-table">
                      <thead>
                        <tr>
                          <th>Proyecto</th>
                          <th>Fecha y Hora</th>
                          <th>Puntaje Global</th>
                          <th>Nivel de Calidad</th>
                          <th>Hallazgos</th>
                          <th>Acción</th>
                          <th>Reporte</th>
                        </tr>
                      </thead>
                      <tbody>
                        {paginatedRuns.map((run) => (
                          <tr 
                            key={run.id} 
                            className={selectedRun?.id === run.id ? "active-row" : ""}
                            onClick={() => handleSelectRun(run)}
                          >
                            <td>
                              <strong>{run.projects?.project_name || "Proyecto Principal"}</strong>
                            </td>
                            <td>{new Date(run.created_at).toLocaleString("es-ES")}</td>
                            <td>
                              <span className={`score-badge ${getScoreClass(run.global_score)}`}>
                                {run.global_score}/100
                              </span>
                            </td>
                            <td>
                              <strong>{run.quality_level}</strong>
                            </td>
                            <td>{run.total_findings} hallazgos</td>
                            <td>
                              <button className="view-details-btn">
                                {selectedRun?.id === run.id ? "Visualizando" : "Ver detalles"}
                              </button>
                            </td>
                            <td>
                              <button 
                                className="icon-btn" 
                                style={{ 
                                  padding: '8px', 
                                  width: '36px', 
                                  height: '36px', 
                                  display: 'flex', 
                                  alignItems: 'center', 
                                  justifyContent: 'center',
                                  borderRadius: '6px',
                                  backgroundColor: 'transparent',
                                  border: 'none',
                                  color: '#000',
                                  cursor: generatingPdfId === run.id ? 'not-allowed' : 'pointer',
                                  opacity: generatingPdfId === run.id ? 0.5 : 1
                                }}
                                disabled={generatingPdfId === run.id}
                                onClick={(e) => handleDownloadReport(run, e)}
                                title="Descargar Reporte PDF"
                              >
                                {generatingPdfId === run.id ? (
                                  <span style={{ fontSize: '0.75rem', color: '#000' }}>...</span>
                                ) : (
                                  <svg 
                                    xmlns="http://www.w3.org/2000/svg" 
                                    width="20" 
                                    height="20" 
                                    viewBox="0 0 24 24" 
                                    fill="none" 
                                    stroke="#000000" 
                                    strokeWidth="2.5" 
                                    strokeLinecap="round" 
                                    strokeLinejoin="round"
                                  >
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                    <polyline points="7 10 12 15 17 10"></polyline>
                                    <line x1="12" y1="15" x2="12" y2="3"></line>
                                  </svg>
                                )}
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Controles de Paginación */}
                  {filteredRuns.length > itemsPerPage && (
                    <div className="pagination-controls">
                      <button
                        className="pagination-btn"
                        disabled={currentPage === 1}
                        onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                      >
                        Anterior
                      </button>
                      <span className="pagination-info">
                        Página {currentPage} de {totalPages}
                      </span>
                      <button
                        className="pagination-btn"
                        disabled={currentPage === totalPages}
                        onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                      >
                        Siguiente
                      </button>
                    </div>
                  )}
                </>
              )}
            </section>

            {/* Detalle del Análisis Seleccionado */}
            {selectedRun && (
              <div className="modal-overlay" onClick={() => setSelectedRun(null)}>
                <section className="modal-container details-section card fade-in" onClick={(e) => e.stopPropagation()}>
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

                  <div className="summary-cards">
                    <div className="summary-card">
                      <span>Puntaje Global</span>
                      <strong className={getScoreClass(selectedRun.global_score)}>
                        {selectedRun.global_score}
                      </strong>
                    </div>
                    <div className="summary-card">
                      <span>Nivel de Calidad</span>
                      <strong>{selectedRun.quality_level}</strong>
                    </div>
                    <div className="summary-card">
                      <span>Hallazgos Totales</span>
                      <strong>{selectedRun.total_findings}</strong>
                    </div>
                  </div>

                  <h3>Hallazgos Técnicos Registrados</h3>

                  {loadingFindings ? (
                    <div className="loading-box-small">Cargando hallazgos...</div>
                  ) : findings.length === 0 ? (
                    <div className="success-box">
                      No se detectaron hallazgos técnicos en este análisis.
                    </div>
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

