import { useEffect, useMemo, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { evaluateHtml } from "../services/api";
import "./Evaluation.css";

const TYPE_COLORS = {
  html:     { bg: "#ecfdf5", color: "#047857", label: "HTML"     },
  jsx:      { bg: "#eff6ff", color: "#1d4ed8", label: "JSX"      },
  tsx:      { bg: "#f5f3ff", color: "#6d28d9", label: "TSX"      },
  ts:       { bg: "#fdf4ff", color: "#7e22ce", label: "TS"       },
  js:       { bg: "#fefce8", color: "#92400e", label: "JS"       },
  vue:      { bg: "#f0fdf4", color: "#15803d", label: "VUE"      },
  svelte:   { bg: "#fff7ed", color: "#c2410c", label: "SVELTE"   },
  astro:    { bg: "#faf5ff", color: "#7c3aed", label: "ASTRO"    },
  cshtml:   { bg: "#f0f9ff", color: "#0369a1", label: "CSHTML"   },
  razor:    { bg: "#f0f9ff", color: "#0369a1", label: "RAZOR"    },
  php:      { bg: "#f5f3ff", color: "#5b21b6", label: "PHP"      },
  blade:    { bg: "#fdf2f8", color: "#9d174d", label: "BLADE"    },
  erb:      { bg: "#fef2f2", color: "#991b1b", label: "ERB"      },
  hbs:      { bg: "#fff8f0", color: "#c2410c", label: "HBS"      },
  mustache: { bg: "#fff8f0", color: "#c2410c", label: "MUSTACHE" },
  ejs:      { bg: "#f0fdf4", color: "#166534", label: "EJS"      },
  pug:      { bg: "#f9fafb", color: "#374151", label: "PUG"      },
  jinja:    { bg: "#fefce8", color: "#854d0e", label: "JINJA"    },
  njk:      { bg: "#fefce8", color: "#854d0e", label: "NJK"      },
  twig:     { bg: "#f0fdf4", color: "#065f46", label: "TWIG"     },
  liquid:   { bg: "#eff6ff", color: "#1e40af", label: "LIQUID"   },
  combined: { bg: "#f1f5f9", color: "#334155", label: "FULL"     },
};

function TypeBadge({ type }) {
  const t = TYPE_COLORS[type] || TYPE_COLORS.combined;
  return (
    <span
      className="type-badge"
      style={{ background: t.bg, color: t.color }}
    >
      {t.label}
    </span>
  );
}

export default function Evaluation() {
  const navigate = useNavigate();

  const [evaluationResult, setEvaluationResult] = useState(null);
  const [htmlToEvaluate, setHtmlToEvaluate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [captureResult, setCaptureResult] = useState(null);
  const [selectedIface, setSelectedIface] = useState(null);
  const [evaluationCache, setEvaluationCache] = useState({});

  const hasCalled = useRef(false);

  const isZip = captureResult?.source_type === "zip";
  const interfaces = useMemo(() => {
    if (!captureResult?.interfaces || !Array.isArray(captureResult.interfaces)) return [];
    return captureResult.interfaces;
  }, [captureResult]);

  useEffect(() => {
    const savedEvaluation = localStorage.getItem("isoEvaluation");
    const savedHtml = localStorage.getItem("htmlToEvaluate");
    const savedCapture = localStorage.getItem("captureResult");

    let localIsZip = false;
    let parsedCapture = null;
    if (savedCapture) {
      try {
        parsedCapture = JSON.parse(savedCapture);
        setCaptureResult(parsedCapture);
        localIsZip = parsedCapture.source_type === "zip";
      } catch (err) {
        console.error(err);
      }
    }

    if (!savedHtml) {
      setError("No se encontró HTML para evaluar. Regrese a la réplica HTML.");
      return;
    }

    setHtmlToEvaluate(savedHtml);

    let initialIface = null;
    if (localIsZip && parsedCapture && parsedCapture.interfaces) {
      initialIface = parsedCapture.interfaces.find(
        (iface) => iface.html_content === savedHtml
      ) || null;
    }
    setSelectedIface(initialIface);

    const cacheKey = initialIface ? initialIface.file_name : "combined";

    if (savedEvaluation) {
      try {
        const parsedEval = JSON.parse(savedEvaluation);
        setEvaluationResult(parsedEval);
        setEvaluationCache({
          [cacheKey]: parsedEval
        });
        return;
      } catch (err) {
        console.error(err);
      }
    }

    if (hasCalled.current) return;
    hasCalled.current = true;

    runEvaluation(savedHtml, cacheKey);
  }, []);

  const runEvaluation = async (html, cacheKey) => {
    try {
      setLoading(true);
      setError("");

      const result = await evaluateHtml(html);

      setEvaluationResult(result);
      setEvaluationCache(prev => ({
        ...prev,
        [cacheKey]: result
      }));
      localStorage.setItem("isoEvaluation", JSON.stringify(result));
    } catch (err) {
      setError(
        "No se pudo ejecutar la evaluación ISO/IEC 25010. Verifique que el backend esté encendido."
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = async (iface) => {
    setSelectedIface(iface);
    setError("");
    setEvaluationResult(null);
    localStorage.removeItem("technicalReport"); // Clear cached report for old tab

    const targetHtmlContent = iface
      ? iface.html_content
      : captureResult?.html_content || "";

    if (!targetHtmlContent.trim()) {
      setError("No existe contenido HTML para evaluar en esta interfaz.");
      return;
    }

    const cacheKey = iface ? iface.file_name : "combined";
    if (evaluationCache[cacheKey]) {
      const cached = evaluationCache[cacheKey];
      setEvaluationResult(cached);
      localStorage.setItem("isoEvaluation", JSON.stringify(cached));
      return;
    }

    await runEvaluation(targetHtmlContent, cacheKey);
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

  const scoreItems = [
    {
      label: "Adecuación funcional",
      key: "adecuacion_funcional",
      value: scores.adecuacion_funcional ?? 0,
    },
    {
      label: "Eficiencia de desempeño",
      key: "eficiencia_desempeno",
      value: scores.eficiencia_desempeno ?? 0,
    },
    {
      label: "Usabilidad",
      key: "usabilidad",
      value: scores.usabilidad ?? 0,
    },
    {
      label: "Accesibilidad",
      key: "accesibilidad",
      value: scores.accesibilidad ?? 0,
    },
    {
      label: "Mantenibilidad",
      key: "mantenibilidad",
      value: scores.mantenibilidad ?? 0,
    },
    {
      label: "Compatibilidad",
      key: "compatibilidad",
      value: scores.compatibilidad ?? 0,
    },
    {
      label: "Seguridad",
      key: "seguridad",
      value: scores.seguridad ?? 0,
    },
    {
      label: "Portabilidad",
      key: "portabilidad",
      value: scores.portabilidad ?? 0,
    },
  ];

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
    localStorage.removeItem("isoEvaluation");
    runEvaluation(htmlToEvaluate);
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="evaluation-main">
        <section className="page-header">
          <p className="page-kicker">Agente de Evaluación ISO/IEC 25010</p>
          <h1 className="page-title">Diagnóstico técnico de calidad frontend</h1>
          <p className="page-description">
            El agente crítico analiza el HTML evaluable y calcula puntajes de
            calidad por dimensión, hallazgos técnicos, severidades y
            recomendaciones según criterios de ISO/IEC 25010 y accesibilidad web.
          </p>
        </section>

        {/* ── Interface Tabs (ZIP only) ───────────────── */}
        {isZip && interfaces.length > 0 && (
          <nav className="tabs-navigation" style={{ marginBottom: "22px" }}>
            <button
              type="button"
              className={`tab-btn ${!selectedIface ? "tab-btn--active" : ""}`}
              onClick={() => handleTabChange(null)}
            >
              <TypeBadge type="combined" />
              <span>Paquete completo</span>
            </button>

            {interfaces.map((iface, i) => (
              <button
                key={i}
                type="button"
                className={`tab-btn ${selectedIface?.file_name === iface.file_name ? "tab-btn--active" : ""}`}
                onClick={() => handleTabChange(iface)}
              >
                <TypeBadge type={iface.type} />
                <span>{iface.file_name}</span>
              </button>
            ))}
          </nav>
        )}

        {error && <div className="error-box">{error}</div>}

        {loading && (
          <div className="loading-box">
            Ejecutando reglas de evaluación ISO/IEC 25010. Espere unos
            segundos...
          </div>
        )}

        {!loading && evaluationResult && (
          <>
            <section className="evaluation-hero card">
              <div className="score-circle-wrapper">
                <div className={`score-circle ${getScoreClass(globalScore)}`}>
                  <strong>{globalScore}</strong>
                  <span>/100</span>
                </div>
              </div>

              <div className="evaluation-hero-content">
                <span className="result-label">Puntaje global</span>
                <h2>{qualityLevel}</h2>
                <p>
                  El puntaje global representa el nivel de calidad técnica de la
                  interfaz frontend evaluada, considerando eficiencia,
                  usabilidad, accesibilidad, mantenibilidad, compatibilidad,
                  seguridad y portabilidad.
                </p>
              </div>

              <div className="findings-total">
                <span>Total de hallazgos</span>
                <strong>{totalFindings}</strong>
              </div>
            </section>

            <section className="severity-grid">
              <article className="severity-card card critical">
                <span>Críticas</span>
                <strong>{severityCount.Crítica || 0}</strong>
              </article>

              <article className="severity-card card high">
                <span>Altas</span>
                <strong>{severityCount.Alta || 0}</strong>
              </article>

              <article className="severity-card card medium">
                <span>Medias</span>
                <strong>{severityCount.Media || 0}</strong>
              </article>

              <article className="severity-card card low">
                <span>Bajas</span>
                <strong>{severityCount.Baja || 0}</strong>
              </article>
            </section>

            <section className="scores-section card">
              <div className="section-header">
                <h2>Puntajes por dimensión ISO/IEC 25010</h2>
                <p>
                  Cada dimensión se calcula sobre una escala de 0 a 100,
                  aplicando penalizaciones por deficiencias detectadas.
                </p>
              </div>

              <div className="score-list">
                {scoreItems.map((item) => (
                  <div className="score-row" key={item.key}>
                    <div className="score-row-label">
                      <strong>{item.label}</strong>
                      <span>{item.value}/100</span>
                    </div>

                    <div className="score-bar">
                      <div
                        className="score-bar-fill"
                        style={{ width: `${item.value}%`, background: "#000000" }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="findings-section card">
              <div className="section-header">
                <h2>Hallazgos técnicos detectados</h2>
                <p>
                  Los hallazgos se clasifican por dimensión, subdimensión y
                  severidad para orientar la toma de decisiones técnicas.
                </p>
              </div>

              {findings.length > 0 ? (
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
                        <tr key={index}>
                          <td>{index + 1}</td>
                          <td>{item.dimension || "No especificada"}</td>
                          <td>{item.subdimension || "No especificada"}</td>
                          <td>
                            <span
                              className={`severity-pill ${getSeverityClass(
                                item.severity
                              )}`}
                            >
                              {item.severity || "Media"}
                            </span>
                          </td>
                          <td>{item.finding || "Hallazgo no especificado."}</td>
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
                    Sugerencias generales para mejorar la calidad frontend del
                    artefacto evaluado.
                  </p>
                </div>

                <ul>
                  {evaluation.engineering_tips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </section>
            )}

            <div className="page-actions">
              <button className="secondary-btn" type="button" onClick={goBack}>
                Volver
              </button>

              <button className="secondary-btn" type="button" onClick={reevaluate}>
                Reevaluar
              </button>

              <button
                className="primary-btn"
                type="button"
                onClick={continueToReport}
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