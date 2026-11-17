import { useEffect, useMemo, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { evaluateHtml } from "../services/api";
import { storageService } from "../services/storageService";
import NormativeSection from "../components/NormativeSection";
import { CORE_CHARACTERISTICS, characteristicRows } from "../utils/isoCharacteristics";
import "./Evaluation.css";

const EXPECTED_KEY = "expectedFunctions";

function readExpected() {
  try {
    return localStorage.getItem(EXPECTED_KEY) || "";
  } catch {
    return "";
  }
}

export default function Evaluation() {
  const navigate = useNavigate();

  const [evaluationResult, setEvaluationResult] = useState(null);
  const [htmlToEvaluate, setHtmlToEvaluate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [, setCaptureResult] = useState(null);
  const [selectedIface, setSelectedIface] = useState(null);
  const [, setEvaluationCache] = useState({});
  const [includeEfficiency, setIncludeEfficiency] = useState(false);
  const [expectedText, setExpectedText] = useState(readExpected);

  const hasCalled = useRef(false);

  useEffect(() => {
    const savedEvaluation = storageService.getIsoEvaluation();
    const savedHtml = storageService.getHtmlToEvaluate();
    const savedCapture = storageService.getCaptureResult();

    let parsedCapture = null;
    if (savedCapture) {
      parsedCapture = savedCapture;
      setCaptureResult(parsedCapture);
    }

    if (!savedHtml) {
      setError("No se encontró HTML para evaluar. Regrese a la réplica HTML.");
      return;
    }

    setHtmlToEvaluate(savedHtml);

    let initialIface = null;
    if (parsedCapture && parsedCapture.interfaces) {
      initialIface = parsedCapture.interfaces.find(
        (iface) => iface.html_content === savedHtml
      ) || null;
    }
    setSelectedIface(initialIface);

    const cacheKey = initialIface ? initialIface.file_name : "combined";

    if (savedEvaluation) {
      let allEvals = {};
      const savedAllEvals = storageService.getItem("isoEvaluations");
      if (savedAllEvals) {
          allEvals = savedAllEvals;
      }
      
      setEvaluationResult(savedEvaluation);
      
      const initialCache = {
        ...allEvals,
        [cacheKey]: savedEvaluation
      };
      setEvaluationCache(initialCache);
      storageService.setItem("isoEvaluations", initialCache);
      return;
    }

    if (hasCalled.current) return;
    hasCalled.current = true;

    runEvaluation(savedHtml, cacheKey, initialIface);
  }, []);

  const runEvaluation = async (html, cacheKey, iface = selectedIface, options = {}) => {
    try {
      setLoading(true);
      setError("");

      // Métricas y evidencias de ejecución de la interfaz evaluada (o de la principal)
      const capture = storageService.getCaptureResult();
      const runtimeMetrics =
        iface?.performance_metrics || capture?.selected_interface?.performance_metrics
        || capture?.performance_metrics || null;
      const evidence =
        iface?.quality_evidence || capture?.selected_interface?.quality_evidence
        || capture?.quality_evidence || null;
      const withEfficiency = options.includeEfficiency ?? includeEfficiency;
      const characteristics = withEfficiency ? [...CORE_CHARACTERISTICS, "eficiencia_desempeno"] : null;
      const expected = (options.expectedText ?? expectedText)
        .split(/\r?\n/).map((line) => line.trim()).filter(Boolean).slice(0, 50);
      const result = await evaluateHtml(html, runtimeMetrics, characteristics, evidence, expected);

      // Assign the interface name to the evaluation result so the ReportAgent knows it
      if (result && result.evaluation) {
          result.evaluation.name = cacheKey;
      }
      
      setEvaluationResult(result);
      setEvaluationCache(prev => {
        const updated = {
          ...prev,
          [cacheKey]: result
        };
        storageService.setItem("isoEvaluations", updated);
        return updated;
      });
      storageService.setIsoEvaluation(result);
    } catch {
      setError(
        "No se pudo ejecutar la evaluación ISO/IEC 25010. Verifique que el backend esté encendido."
      );
      
    } finally {
      setLoading(false);
    }
  };

  const evaluation = useMemo(() => {
    return evaluationResult?.evaluation || evaluationResult || {};
  }, [evaluationResult]);

  const scores = useMemo(() => {
    return evaluation?.scores || {};
  }, [evaluation]);

  const findings = useMemo(() => {
    if (!evaluation?.findings || !Array.isArray(evaluation.findings)) {
      return [];
    }

    return evaluation.findings;
  }, [evaluation]);

  const globalScore = evaluation?.global_score ?? 0;
  const qualityLevel = evaluation?.quality_level || "No calculado";
  const totalFindings = evaluation?.total_findings ?? findings.length;

  const scoreItems = characteristicRows(scores, evaluation?.not_evaluated || []);

  const severityCount = useMemo(() => {
    const result = {
      Alta: 0,
      Media: 0,
      Baja: 0,
      Crítica: 0,
    };

    findings.forEach((item) => {
      const severity = item.severity || "Media";

      if (result[severity] === undefined) {
        result[severity] = 0;
      }

      result[severity] += 1;
    });

    return result;
  }, [findings]);

  const getSeverityClass = (severity) => {
    if (severity === "Crítica") return "critical";
    if (severity === "Alta") return "high";
    if (severity === "Media") return "medium";
    return "low";
  };

  const goBack = () => {
    navigate("/html");
  };

  const continueToReport = () => {
    if (!evaluationResult) {
      setError("No existe una evaluación para generar el reporte.");
      return;
    }

    navigate("/report");
  };

  const reevaluate = () => {
    storageService.removeItem("isoEvaluation");
    try {
      localStorage.setItem(EXPECTED_KEY, expectedText);
    } catch {
      // localStorage no disponible: el texto sólo se usa en esta evaluación
    }
    const cacheKey = selectedIface ? selectedIface.file_name : "combined";
    runEvaluation(htmlToEvaluate, cacheKey, selectedIface);
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="evaluation-main">
        <header className="page-header eval-header">
          <div className="eval-header-left">
            <div className="eval-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
            <div>
              <h1 className="page-title">Diagnóstico técnico de calidad frontend</h1>
              <p className="page-description" style={{ margin: "6px 0 0" }}>Evaluación del código frontend según los criterios de la norma ISO/IEC 25010, con análisis de buenas prácticas, accesibilidad, rendimiento y más.</p>
            </div>
          </div>
          <div className="eval-header-right">
            <span>Informe de evaluación</span>
            <strong>Frontend</strong>
          </div>
        </header>

        {error && <div className="error-box">{error}</div>}

        {loading && (
          <div className="loading-box">
            Ejecutando reglas de evaluación ISO/IEC 25010. Espere unos segundos...
          </div>
        )}

        {!loading && evaluationResult && (
          <>
            <section className="top-dashboard-card card">
              <div className="top-dashboard-left">
                <div className="score-circle-wrapper">
                  <div className={`score-circle score-blue`}>
                    <strong>{globalScore}</strong>
                    <span>/100</span>
                  </div>
                </div>
                <div className="evaluation-hero-content">
                  <span className="result-label">PUNTAJE GLOBAL</span>
                  <h2>{qualityLevel}</h2>
                  <p>
                    Nivel de calidad: {qualityLevel.toLowerCase()}. Promedio de las
                    características evaluadas de ISO/IEC 25010:2023 (adecuación
                    funcional, capacidad de interacción, compatibilidad, flexibilidad,
                    seguridad y fiabilidad{includeEfficiency ? " y eficiencia de desempeño" : ""}).
                  </p>
                </div>
              </div>

              <div className="top-dashboard-center">
                <div className="severity-row">
                  <div className="severity-item critical">
                    <span>CRÍTICAS</span>
                    <strong>{severityCount.Crítica || 0}</strong>
                  </div>
                  <div className="severity-item high">
                    <span>ALTAS</span>
                    <strong>{severityCount.Alta || 0}</strong>
                  </div>
                  <div className="severity-item medium">
                    <span>MEDIAS</span>
                    <strong>{severityCount.Media || 0}</strong>
                  </div>
                  <div className="severity-item low">
                    <span>BAJAS</span>
                    <strong>{severityCount.Baja || 0}</strong>
                  </div>
                </div>
              </div>

              <div className="top-dashboard-right">
                <div className="findings-total-box">
                  <span>TOTAL DE HALLAZGOS</span>
                  <strong>{totalFindings}</strong>
                </div>
              </div>
            </section>

            <section className="scores-section card">
              <div className="section-header">
                <h2>Parámetros de la evaluación</h2>
                <p>
                  La completitud y pertinencia funcional sólo pueden medirse frente a una especificación:
                  escriba las funciones que la interfaz debe ofrecer (una por línea, p. ej. «Iniciar sesión»).
                </p>
              </div>
              <label htmlFor="expected-functions" style={{ display: "block", fontWeight: 600, marginBottom: 6 }}>
                Funciones esperadas
              </label>
              <textarea
                id="expected-functions"
                rows={4}
                value={expectedText}
                onChange={(event) => setExpectedText(event.target.value)}
                placeholder={"Iniciar sesión\nRegistrarse\nBuscar"}
                style={{ width: "100%", boxSizing: "border-box", padding: 10, borderRadius: 8, border: "1px solid #cbd5e1", fontFamily: "inherit" }}
              />
              <label style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 12 }}>
                <input
                  type="checkbox"
                  checked={includeEfficiency}
                  onChange={(event) => setIncludeEfficiency(event.target.checked)}
                />
                Incluir eficiencia de desempeño (opcional)
              </label>
              <button className="secondary-btn" type="button" onClick={reevaluate} style={{ width: "auto", marginTop: 12 }}>
                Aplicar y reevaluar
              </button>
            </section>

            <section className="scores-section card">
              <div className="section-header">
                <h2>Puntajes por dimensión ISO/IEC 25010</h2>
                <p>
                  Cada puntaje es el promedio ponderado del cumplimiento de sus métricas medidas.
                  Una característica sin evidencia suficiente figura como «No evaluada» y no entra al puntaje global.
                </p>
              </div>

              <div className="score-list">
                {scoreItems.map((item) => (
                  <div className="score-row" key={item.key}>
                    <div className="score-row-label">
                      <strong>{item.label}</strong>
                      <span>{item.value === null ? "No evaluada" : `${item.value}/100`}</span>
                    </div>

                    <div className="score-bar">
                      <div
                        className="score-bar-fill"
                        style={{ width: `${item.value ?? 0}%`, background: "#1e3a8a" }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="findings-section card">
              <div className="section-header">
                <h2>Hallazgos técnicos</h2>
                <p>
                  Los hallazgos se clasifican por dimensión, con su respectiva severidad y recomendación de solución.
                </p>
              </div>

              {findings.length > 0 ? (
                <div className="findings-table-wrapper">
                  <table className="findings-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>DIMENSIÓN</th>
                        <th>CRITERIO</th>
                        <th>SEVERIDAD</th>
                        <th>DESCRIPCIÓN</th>
                        <th>RECOMENDACIÓN</th>
                      </tr>
                    </thead>

                    <tbody>
                      {findings.map((item, index) => (
                        <tr key={index}>
                          <td>{item.metric_id || index + 1}</td>
                          <td>{item.dimension || "No especificada"}</td>
                          <td>{item.subdimension || "No especificada"}</td>
                          <td>
                            <span
                              className={`severity-pill ${getSeverityClass(
                                item.severity
                              )}`}
                            >
                              {item.severity?.toUpperCase() || "MEDIA"}
                            </span>
                            {item.severity_grade_label && (
                              <small style={{ display: "block", marginTop: "4px", color: "#64748b" }}>
                                Grado {item.severity_grade} · {item.severity_grade_label}
                              </small>
                            )}
                          </td>
                          <td>{item.finding?.replace(/\[.*?\]\s*/g, '') || "Hallazgo no especificado."}</td>
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

            {evaluation?.engineering_tips?.length > 0 && (
              <section className="tips-section card">
                <div className="section-header">
                  <h2>Recomendaciones de ingeniería</h2>
                  <p>
                    Sugerencias generales para mejorar la calidad frontend del proyecto evaluado.
                  </p>
                </div>

                <div className="findings-table-wrapper">
                  <table className="findings-table">
                    <thead>
                      <tr>
                        <th>PRIORIDAD</th>
                        <th>RECOMENDACIÓN</th>
                        <th>ACCIÓN SUGERIDA / ALCANCE</th>
                      </tr>
                    </thead>
                    <tbody>
                      {evaluation.engineering_tips.map((tip, index) => {
                        let prioridad = "Media";
                        let recomendacion = tip;
                        let accion = "Revisar implementación y ajustar según buenas prácticas.";
                        
                        if (index === 0) prioridad = "Alta";
                        else if (index > 2) prioridad = "Baja";

                        return (
                          <tr key={index}>
                            <td>
                              <span className={`severity-pill ${getSeverityClass(prioridad)}`}>
                                {prioridad.toUpperCase()}
                              </span>
                            </td>
                            <td>{recomendacion}</td>
                            <td>{accion}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            <NormativeSection data={evaluation} />

            <div className="page-actions" style={{ justifyContent: "flex-start", gap: "16px", padding: "0 26px" }}>
              <button className="secondary-btn" type="button" onClick={goBack} style={{ width: "auto" }}>
                ← Volver
              </button>

              <button className="secondary-btn" type="button" onClick={reevaluate} style={{ width: "auto" }}>
                ↻ Reevaluar
              </button>

              <button
                className="primary-btn"
                type="button"
                onClick={continueToReport}
                style={{ width: "auto", background: "#2563eb", marginLeft: "10px" }}
              >
                Generar reporte
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}